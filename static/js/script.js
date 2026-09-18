let login_btn = document.getElementById('h-login-btn');
let register_btn = document.getElementById('h-register-btn');
const redirect=(href)=>{ window.location.href=`/${href}` };
login_btn.addEventListener('click',function(ev){ redirect('auth?mode=login'); });
register_btn.addEventListener('click',function(ev){ redirect('auth?mode=register'); });