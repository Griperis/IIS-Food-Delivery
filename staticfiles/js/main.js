window.onload = () => {
    let elems = document.getElementsByClassName('reload-scroll-back');
    for (let i = 0; i < elems.length; i++) {
        elems[i].addEventListener('submit', () => {
            window.localStorage.setItem('scroll', window.scrollY);
        });
    }
    let url = window.location.href;
    if (url.indexOf('add_item') >= 0 || url.indexOf('remove_item') >= 0) {
        let scrollPos = parseInt(window.localStorage.getItem('scroll'), 10);
        window.scrollTo(0, scrollPos);
        window.localStorage.setItem('scroll', 0);
    }
}

function goto_profile(){
    $('[href="#nav-profile"]').tab('show');
}

