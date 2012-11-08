---
title:
chinese: '国庆自驾游方案'
date: '2012-09-21'
description:
categories:
layout: 'gap'
tasks : true
---
1. 300公里以内
2. 三天两夜或四天三夜
3. 人尽量少

<div>
    <h3>浙江遗珠</h3>
    <pre><code id="zj-obscure"></code></pre>
    <h3>江苏遗珠</h3>
    <pre><code id="js-obscure"></code></pre>
</div>
<div>
    <script src="/assets/twitter/javascripts/wind-all-0.7.3.js"></script>
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
                      failures: getJSONAsync('/data/national-forest-park/geocode-fail.json'),
                      zhejiang: getJSONAsync('/data/national-forest-park/zhejiang.json'),
                      jiangsu: getJSONAsync('/data/national-forest-park/jiangsu.json')
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