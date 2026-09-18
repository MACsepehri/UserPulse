var login_form = document.getElementById('login-form');
var mode = document.getElementsByName('action_mode')[0];

document.getElementById('continue-btn').addEventListener('click',function(ev){
    if(mode=='login') {
        var usrname = document.getElementsByName('usrname')[0].value.trim();
        var password = document.getElementsByName('password')[0].value.trim();
        if(usrname==''||password==''){ alert('مقادیر نامعتبر'); return 0; }
    } else {
        var usrname = document.getElementsByName('usrname')[0].value.trim();
        var password = document.getElementsByName('password')[0].value.trim();
        var email = document.getElementsByName('email')[0].value.trim();
        if(usrname==''||password==''||email==''){ alert('مقادیر نامعتبر'); return 0; }
    }
    login_form.submit();
})