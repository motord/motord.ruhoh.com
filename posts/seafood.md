---
title:
chinese: '铜川水产市场价格行情'
date: '2012-10-23'
description:
categories: tools
tags: ['data', 'visualization']
---
<div id="market">
</div>
<div>
    <script src="/assets/twitter/javascripts/jquery-1.8.1.min.js"></script>
    <script src="/assets/twitter/javascripts/underscore-min.js"></script>
    <script src="/assets/twitter/javascripts/wind-all-0.7.3.js"></script>
    <script src="/assets/twitter/javascripts/raphael-min.js"></script>
    <script src="/assets/twitter/javascripts/morris.min.js"></script>
    <script src="/assets/twitter/javascripts/json-to-table.js"></script>
    <script type="text/javascript">
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
        var composeJavascriptLink = function(message) {
            js= "javascript:console.log('{0}');";
            return js.format(message);
        };
        var intepretJavascriptLink = function(url) {
            var pattern=/^javascript:console.log\(\'([\s\S]*)\'\);$/;
            var message=url.match(pattern)[1];
            var link = '<a href="{0}">' + message + '</a>';
            return link.format(url);
        };
        var populateAsync = eval(Wind.compile("async", function () {
               var data=$await(intersectAsync());
               var json=_.map(data.market, function(num){ return {'product': composeJavascriptLink(num.fish), 'price': num.price, 'date': num.date}; });
               $("#market").html(ConvertJsonToTable(json, 'jsonTable', 'table table-striped table-condensed', intepretJavascriptLink));
         }));
         populateAsync().start();
    </script>
</div>