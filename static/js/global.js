const toggler = document.querySelector('.navbar-toggler');
if (toggler) {

    toggler.offsetHeight;

    window.dispatchEvent(new Event('resize'));
}
