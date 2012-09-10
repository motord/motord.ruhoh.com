/**
 * Created with PyCharm.
 * User: peter
 * Date: 9/10/12
 * Time: 3:05 PM
 * To change this template use File | Settings | File Templates.
 */
// An example Backbone application contributed by
// [Jérôme Gravel-Niquet](http://jgn.me/). This demo uses a simple
// [LocalStorage adapter](backbone-localstorage.html)
// to persist Backbone models within your browser.

// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

    // Task Model
    // ----------

    // Our basic **Task** model has `todo`, `created`, and `accomplished` attributes.
    window.Task = Backbone.Model.extend({

        // If you don't provide a task, one will be provided for you.
        EMPTY: "empty task...",

        // Ensure that each task created has `todo`.
        initialize: function() {
            if (!this.get("todo")) {
                this.set({"todo": this.EMPTY});
            }
        },

        // Toggle the `accomplished` state of this task item.
        toggle: function() {
            this.save({accomplished: !this.get("accomplished")});
        },

        // Remove this Task from *localStorage* and delete its view.
        clear: function() {
            this.destroy();
            this.view.remove();
        }

    });

    // Task Collection
    // ---------------

    // The collection of tasks is backed by *localStorage* instead of a remote
    // server.
    window.TaskList = Backbone.Collection.extend({

        // Reference to this collection's model.
        model: Task,

        // Save all of the task items under the `"tasks"` namespace.
        //localStorage: new Store("tasks"),

        url: '/api/',

        // Filter down the list of all task items that are finished.
        accomplished: function() {
            return this.filter(function(task){ return task.get('accomplished'); });
        },

        // Filter down the list to only task items that are still not finished.
        remaining: function() {
            return this.without.apply(this, this.accomplished());
        },

        // Tasks are sorted by their original insertion order.
        comparator: function(task) {
            return task.get('id');
        }

    });

    // Create our global collection of **Tasks**.
    window.Tasks = new TaskList;

    // Task Item View
    // --------------

    // The DOM element for a task item...
    window.TaskView = Backbone.View.extend({

        //... is a list tag.
        tagName:  "li",

        // Cache the template function for a single item.
        template: _.template($('#item-template').html()),

        // The DOM events specific to an item.
        events: {
            "click .check"              : "toggleAccomplished",
            "dblclick div.task-content" : "edit",
            "click span.task-destroy"   : "clear",
            "keypress .task-input"      : "updateOnEnter"
        },

        // The TaskView listens for changes to its model, re-rendering. Since there's
        // a one-to-one correspondence between a **Task** and a **TaskView** in this
        // app, we set a direct reference on the model for convenience.
        initialize: function() {
            _.bindAll(this, 'render', 'close');
            this.model.bind('change', this.render);
            this.model.view = this;
        },

        // Re-render the contents of the task item.
        render: function() {
            $(this.el).html(this.template(this.model.toJSON()));
            this.setTodo();
            return this;
        },

        // To avoid XSS (not that it would be harmful in this particular app),
        // we use `jQuery.text` to set the contents of the task item.
        setTodo: function() {
            var todo = this.model.get('todo');
            this.$('.task-content').text(todo);
            this.input = this.$('.task-input');
            this.input.bind('blur', this.close);
            this.input.val(todo);
        },

        // Toggle the `"accomplished"` state of the model.
        toggleAccomplished: function() {
            this.model.toggle();
        },

        // Switch this view into `"editing"` mode, displaying the input field.
        edit: function() {
            $(this.el).addClass("editing");
            this.input.focus();
        },

        // Close the `"editing"` mode, saving changes to the task.
        close: function() {
            this.model.save({todo: this.input.val()});
            $(this.el).removeClass("editing");
        },

        // If you hit `enter`, we're through editing the item.
        updateOnEnter: function(e) {
            if (e.keyCode == 13) this.close();
        },

        // Remove this view from the DOM.
        remove: function() {
            $(this.el).remove();
        },

        // Remove the item, destroy the model.
        clear: function() {
            this.model.clear();
        }

    });

    // The Application
    // ---------------

    // Our overall **AppView** is the top-level piece of UI.
    window.AppView = Backbone.View.extend({

        // Instead of generating a new element, bind to the existing skeleton of
        // the App already present in the HTML.
        el: $("#taskapp"),

        // Our template for the line of statistics at the bottom of the app.
        statsTemplate: _.template($('#stats-template').html()),

        // Delegated events for creating new items, and clearing completed ones.
        events: {
            "keypress #new-task":  "createOnEnter",
            "keyup #new-task":     "showTooltip",
            "click .task-clear a": "clearCompleted"
        },

        // At initialization we bind to the relevant events on the `Tasks`
        // collection, when items are added or changed. Kick things off by
        // loading any preexisting tasks that might be saved in *localStorage*.
        initialize: function() {
            _.bindAll(this, 'addOne', 'addAll', 'render');

            this.input    = this.$("#new-task");

            Tasks.bind('add',     this.addOne);
            Tasks.bind('refresh', this.addAll);
            Tasks.bind('all',     this.render);

            Tasks.fetch();
        },

        // Re-rendering the App just means refreshing the statistics -- the rest
        // of the app doesn't change.
        render: function() {
            var accomplished = Tasks.accomplished().length;
            this.$('#task-stats').html(this.statsTemplate({
                total:      Tasks.length,
                accomplished:       Tasks.accomplished().length,
                remaining:  Tasks.remaining().length
            }));
        },

        // Add a single task item to the list by creating a view for it, and
        // appending its element to the `<ul>`.
        addOne: function(task) {
            var view = new TaskView({model: task});
            this.$("#task-list").append(view.render().el);
        },

        // Add all items in the **Tasks** collection at once.
        addAll: function() {
            Tasks.each(this.addOne);
        },

        // Generate the attributes for a new Task item.
        newAttributes: function() {
            return {
                todo: this.input.val(),
                accomplished:    false
            };
        },

        // If you hit return in the main input field, create new **Task** model,
        // persisting it to *localStorage*.
        createOnEnter: function(e) {
            if (e.keyCode != 13) return;
            Tasks.create(this.newAttributes());
            this.input.val('');
        },

        // Clear all done task items, destroying their models.
        clearCompleted: function() {
            _.each(Tasks.accomplished(), function(task){ task.clear(); });
            return false;
        },

        // Lazily show the tooltip that tells you to press `enter` to save
        // a new task item, after one second.
        showTooltip: function(e) {
            var tooltip = this.$(".ui-tooltip-top");
            var val = this.input.val();
            tooltip.fadeOut();
            if (this.tooltipTimeout) clearTimeout(this.tooltipTimeout);
            if (val == '' || val == this.input.attr('placeholder')) return;
            var show = function(){ tooltip.show().fadeIn(); };
            this.tooltipTimeout = _.delay(show, 1000);
        }

    });

    // Finally, we kick things off by creating the **App**.
    window.App = new AppView;

});
