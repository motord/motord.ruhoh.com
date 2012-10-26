---
title:
chinese: '铜川水产市场价格行情'
date: '2012-10-23'
description:
categories: tools
tags: ['data', 'visualization']
---
<div id="market" style="height: 400px; overflow: auto;">
</div>
<div class="modal" id="graphModal" tabindex="-1" role="dialog" aria-labelledby="graphModalLabel" aria-hidden="true" style="display: none">
</div>
<script type="text/template" id="graph-template">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
        <h3 id="graphModalLabel"><%= name %></h3>
      </div>
      <div class="modal-body">
        <div id="morris"></div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-primary" data-dismiss="modal" aria-hidden="true">Close</button>
      </div>
</script>
<div>
    <script src="/assets/twitter/javascripts/jquery-1.8.1.min.js"></script>
    <script src="/assets/twitter/javascripts/bootstrap.min.js"></script>
    <script src="/assets/twitter/javascripts/underscore-min.js"></script>
    <script src="/assets/twitter/javascripts/wind-all-0.7.3.js"></script>
    <script src="/assets/twitter/javascripts/raphael-min.js"></script>
    <script src="/assets/twitter/javascripts/morris.min.js"></script>
    <script src="/assets/twitter/javascripts/json-to-table.js"></script>
    <script type="text/javascript">
    (function(){
        var root=this;
        var Aqua=root.Aqua={};
        var getJSONAsync = function (url) {
            return Wind.Async.Task.create(function (t) {
                $.getJSON(url, function (data) {
                    t.complete("success", data);
                });
            });
        };
        var intersectAsync = eval(Wind.compile("async", function () {
              var data=$await(Wind.Async.Task.whenAll({
                      market: getJSONAsync('/aqua/market.json'),
                      trend: getJSONAsync('/aqua/trend.json')
                  }));
              return {
                  market: data.market,
                  trend: data.trend
              };
        }));
        var trend=Aqua.trend=[];
        Aqua.graph = function(fish) {
            var template=_.template($('#graph-template').html());
            $('#graphModal').html(template({name: fish}));
            $('#graphModal').modal();
            var data=_.find(trend, function(t) { return t.fish==fish});
            var keys=_.sortBy(_.keys(data.prices), function(date){
                return Date(date);
            });
            var plot=[];
            for (i=0; i<keys.length; i++)
            {
                var key=keys[i];
                plot[i]={key:data.prices[key]};
            };
            var plot=_.map(data.prices, function(num){ return {'p': num, 't': key};});
            $('#graphModal').on('shown', function () {
                Morris.Line({
                  element: 'morris',
                  data: plot,
                  xkey: 't',
                  ykeys: ['p'],
                  labels: ['Price']
                });
            });
        };
        var composeJavascriptLink = function(message) {
            js= "javascript:Aqua.graph('{0}');";
            return js.format(message);
        };
        var intepretJavascriptLink = function(url) {
            var pattern=/^javascript:Aqua.graph\(\'([\s\S]*)\'\);$/;
            var message=url.match(pattern)[1];
            var link = '<a class="btn btn-primary" href="{0}">' + message + '</a>';
            return link.format(url);
        };
        var populateAsync = eval(Wind.compile("async", function () {
               var data=$await(intersectAsync());
               var market=_.map(data.market, function(num){ return {'product': composeJavascriptLink(num.fish), 'price': num.price, 'date': num.date}; });
               trend=data.trend;
               $("#market").html(ConvertJsonToTable(market, 'jsonTable', 'table table-striped table-condensed', intepretJavascriptLink));
         }));
         populateAsync().start();
    })();
    </script>
</div>