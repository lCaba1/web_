'use strict';

function modalShown(event) {
    let button = event.relatedTarget;
    let userId = button.dataset.userId

    let rowElements = document.querySelector(`tr[data-user-id="${userId}"]`);

    let firstName = rowElements.children.item(3).textContent;
    let middleName = rowElements.children.item(4).textContent;
    let lastName = rowElements.children.item(2).textContent;
    let userFullName = `${lastName} ${firstName} ${middleName}`;

    let placeToInsertUserData = document.querySelector(`div#deleteModal div.modal-body > p`);
    placeToInsertUserData.innerHTML = userFullName;

    let newUrl = window.location.pathname.replace(/\/+/g, '/').replace(/\/$/, '');
    
    if (!newUrl.includes('/users')) {
        newUrl += '/users';
    }
    
    newUrl += `/${userId}/delete`;
    
    if (!newUrl.startsWith('/')) {
        newUrl = '/' + newUrl;
    }

    let form = document.getElementById('deleteModalForm');
    form.action = newUrl
}

let modal = document.getElementById('deleteModal');
modal.addEventListener('show.bs.modal', modalShown);