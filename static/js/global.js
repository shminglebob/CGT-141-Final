//  Fix hamburger icon disappearing when switching pages
const toggler = document.querySelector('.navbar-toggler');
if (toggler) {
    // read a property that forces a reflow
    toggler.offsetHeight;
    // then nudge it to repaint
    window.dispatchEvent(new Event('resize'));
}