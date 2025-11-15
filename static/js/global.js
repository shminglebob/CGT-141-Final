const toggler = document.querySelector('.navbar-toggler'),
    rootElement = document.documentElement;

if (toggler) {

    toggler.offsetHeight;

    window.dispatchEvent(new Event('resize'));
}