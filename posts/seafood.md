---
title:
chinese: '铜川水产市场价格行情'
date: '2012-10-23'
description:
categories:
---
<div>
    <script src="/assets/twitter/javascripts/jquery-1.8.1.min.js"></script>
    <script src="/assets/twitter/javascripts/underscore-min.js"></script>
    <script src="/assets/twitter/javascripts/wind-all-0.7.3.js"></script>
    <script src="/assets/twitter/javascripts/raphael-min.js"></script>
    <script src="/assets/twitter/javascripts/morris.min.js"></script>
    <script type="text/javascript">
        var getJSONAsync = function (url) {
            return Wind.Async.Task.create(function (t) {
                $.getJSON(url, function (data) {
                    t.complete("success", data);
                });
            });
        };
        var intersectAsync = eval(Wind.compile("async", function () {
              var parks=$await(Wind.Async.Task.whenAll({
                      market: getJSONAsync('/aqua/market.json'),
                      trend: getJSONAsync('/aqua/trend.json'),
                  }));
              return {
                  zj: _.intersection(parks.zhejiang, parks.failures),
                  js: _.intersection(parks.jiangsu, parks.failures)
              };
        }));
        var populateAsync = eval(Wind.compile("async", function () {
               var parks=$await(intersectAsync());
               $("#zj-obscure").html(JSON.stringify(parks.zj));
               $("#js-obscure").html(JSON.stringify(parks.js));
         }));
         populateAsync().start();
    </script>
</div>