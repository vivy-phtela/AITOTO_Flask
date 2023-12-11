function preview(input, imageId) {
    var file = input.files[0];
    var image = document.getElementById(imageId);
    // console.log("Login status:", sessionStorage.getItem('login'));
    
    if (file) {
        var reader = new FileReader();
        reader.onload = function (e) {
            image.src = e.target.result;

            sessionStorage.setItem('previewImage', e.target.result);

            window.location.href = '/preview_page';
        };
        reader.readAsDataURL(file);
    }

}

function noLogin(input, imageId){
    alert('ログインしてください');
}