window.addEventListener('DOMContentLoaded', function () {
    const revertButtons = this.document.querySelectorAll('.revert-button');
    revertButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            const videoName = this.getAttribute('data-video-name');
            const confirmed = confirm("Are you sure you want to revert video '" + videoName + "' to a draft?");
            if (confirmed) {
                fetch('/admin/published/?video_name=' + encodeURIComponent(videoName), {
                    method: 'PUT'
                })
            }
        })
    })

    const pageLinks = this.document.querySelectorAll('.page-link');
    pageLinks.forEach(function (link) {
        link.addEventListener('click', function (event) {
            const page = this.getAttribute('data-page');
            window.location = '/admin/published/?page=' + page;
        })
    })

    const backButton = this.document.querySelector('.back-button');
    backButton.addEventListener('click', function () {
        window.location = '/admin/dashboard/';
    })


    let currentPageNum = this.document.querySelector('.page-num');
    currentPageNum.innerText += new URLSearchParams(window.location.search).get('page') || 0;
    
    const previousButton = this.document.querySelector('.previous-button');
    previousButton.addEventListener('click', function () {
        const currentPageNum = new URLSearchParams(window.location.search).get('page') || 0;
        const previousPageNum = Math.max(0, parseInt(currentPageNum) - 1);
        window.location = '/admin/published/?page=' + previousPageNum;
    })

    const forwardButton = this.document.querySelector('.forward-button');
    forwardButton.addEventListener('click', function () {
        const currentPageNum = new URLSearchParams(window.location.search).get('page') || 0;
        const forwardPageNum = parseInt(currentPageNum) + 1;
        window.location = '/admin/published/?page=' + forwardPageNum;
    })
})