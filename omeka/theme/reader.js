/* Tetrak reader: the transcript tabs in the page viewer's right-hand panel,
   appended to the default theme's script.

   The tabs are radio buttons, since the panel arrives as innerHTML and can
   run no script of its own. But Octopus Viewer cancels every click inside
   the viewer that is not on a link, and a cancelled click on a label never
   reaches its radio button. So the tab is selected here instead, while the
   click is on its way down, before the viewer cancels it. The viewer is a
   shadow root, hence composedPath() for the real target. */
document.addEventListener('click', function (event) {
    var target = event.composedPath()[0];
    var label = target.closest && target.closest('.tr-tabs label');
    if (!label) {
        return;
    }
    var input = label.getRootNode().getElementById(label.htmlFor);
    if (input) {
        input.checked = true;
    }
}, true);
