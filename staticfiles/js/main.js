window.onload = () => {
    let elems = document.getElementsByClassName('reload-scroll-back');
    for (let i = 0; i < elems.length; i++) {
        elems[i].addEventListener('submit', () => {
            window.localStorage.setItem('scroll', window.scrollY);
        });
    }
    let scrollPos = parseInt(window.localStorage.getItem('scroll'), 10);
    window.scrollTo(0, scrollPos);
    window.localStorage.setItem('scroll', 0);
}

function goto_profile(){
    $('[href="#nav-profile"]').tab('show');
}

function goto_tab(type)
{
    if (type == 'offer') 
    {
        $('[href="#nav-offers"]').tab('show')    
    }
    else if (type == 'food')
    {
        $('[href="#nav-foods"]').tab('show')    
    }
    else if (type == 'drink')
    {
        $('[href="#nav-drinks"]').tab('show')    
    }
}