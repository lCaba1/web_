'use strict';

function selectChangeProcess(event) {
    let perPage = event.target.value;
    event.target.parentNode.action = `${window.location.pathname}?per_page=${perPage}`;
    event.target.parentNode.submit();
}

let select = document.getElementById('entries_count');
select.addEventListener('change', selectChangeProcess);