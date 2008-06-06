(function () {
    var href = document.location.href;
    if (href.indexOf("file:") == 0 || !document.getElementsByTagName) return;
    var _old_onload = window.onload;
    window.onload = function () {
        if (_old_onload) _old_onload.call(this);
        _old_onload = null;
        var anchors = document.getElementsByTagName('A');
        var class_re = /\blines-(\d+)-(\d+)\b/;
        var hash_re = /#.*$/;
        for (var i = 0; i < anchors.length; i++) {
            var anchor = anchors[i];
            var found = anchor.className.match(class_re);
            if (!found) continue;
            href = anchor.href;
            var hashidx = href.indexOf("#");
            if (hashidx == -1) hashidx = href.length;
            anchor.href = (href.substring(0, hashidx) + "?f=" + found[1] +
                "&l=" + found[2] + href.substring(hashidx, href.length));
        }
    }
})();
