'use strict';

function selectChangeProcess(event) {
    let perPage = event.target.value;
    // let page = document.getElementById('entries_count').dataset.page;
    // event.target.parentNode.action = `/users/visitor_log?per_page=${perPage}&page=${page}`;
    event.target.parentNode.action = `${window.location.pathname}?per_page=${perPage}`;
    event.target.parentNode.submit();
}

let select = document.getElementById('entries_count');
select.addEventListener('change', selectChangeProcess);