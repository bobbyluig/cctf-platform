$(document).ready(function(){$(".button-collapse").sideNav(),$(".modal-trigger").leanModal(),$("select").material_select(),$("form").submit(function(){return $("#agree").is(":checked")?$("#g-recaptcha-response").val()?(form=$(this),$("button",form).toggleClass("disabled waves-effect waves-light").attr("disabled",!0),$.ajax({type:"POST",url:$(this).attr("action"),data:$(this).serialize(),success:function(e){1==e.success&&(form[0].reset(),form.find("i, label").removeClass("active"),form.find("input").blur()),grecaptcha.reset(),Materialize.toast(e.message,150*e.message.length),setTimeout(function(){$("button",form).toggleClass("disabled waves-effect waves-light").attr("disabled",!1)},500)}}),!1):(Materialize.toast("Please verify your non-bot status.",3e3),!1):(Materialize.toast("Please agree to the Terms and Conditions.",3e3),!1)})});