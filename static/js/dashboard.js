var create_service_form = document.getElementById('create-service-form');

document.getElementById('continue-btn').addEventListener('click',function(ev){
    var service_name = document.getElementsByName('service-name')[0].value.trim();
    var service_desc = document.getElementsByName('service-desc')[0].value.trim();
    if(service_name==''||service_desc==''){ alert('لطفا تمامی مقادیر را وارد کنید.'); return 0; }
    create_service_form.submit();
    return true;
})