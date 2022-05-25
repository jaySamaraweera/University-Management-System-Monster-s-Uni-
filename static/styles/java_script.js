// (function () {
//     'use strict'
//     const forms = document.querySelectorAll('.requires-validation')
//     Array.from(forms)
//       .forEach(function (form) {
//         form.addEventListener('submit', function (event) {
//           if (!form.checkValidity()) {
//             event.preventDefault()
//             event.stopPropagation()
//           }
    
//           form.classList.add('was-validated')
//         }, false)
//       })
//     })()
    
    function validateForm() {
      let id = document.forms["add_user_inputs"]["field_uid"].value;
      if (isNaN(id)) 
      {
        alert("UserID: Must input numbers");
        return false;
      }
      else if (id == 0) 
      {
        alert("UserID: ID can't be 0");
        return false;
      }
      let email = document.forms["add_user_inputs"]["field_email"].value;
      if(!(email.match(/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/)))
      {
        alert("Email: Must be of form xxx@xxx.xxx");
        return false;
      }
      let phone = document.forms["add_user_inputs"]["field_phone"].value;
      if(!(phone.match(/^\(?(\d{3})\)?[- ]?(\d{3})[- ]?(\d{4})$/)))
      {
        alert("Phone Number: Must be of form XXX-XXX-XXXX");
        return false;
      }
      /^\(?(\d{3})\)?[- ]?(\d{3})[- ]?(\d{4})$/
    //   let phone = document.forms["add_user_inputs"]["field_phone"].value;
    //   if (isNaN(phone)) 
    //   {
    //     alert("Phone Number: Must input numbers");
    //     return false;
    //   }
    }

    function reg_validateForm() {
      let reg_email= document.forms["user_register"]["field_email"].value
      if(!(reg_email.match(/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/)))
      {
        alert("Email: Must be of form xxx@xxx.xxx");
        return false;
      }
      let reg_phone = document.forms["user_register"]["field_phone"].value;
      if(!(reg_phone.match(/^\(?(\d{3})\)?[- ]?(\d{3})[- ]?(\d{4})$/)))
      {
        alert("Phone Number: Must be of form XXX-XXX-XXXX");
        return false;
      }
    }

    function students_validateForm() {
      let id = document.forms["s_search"]["student_id"].value;
      console.log("Here");
      if(isNaN(id))
      {
        alert("ID must be an integer");
        return false;
      }
      var fname = document.forms["s_search"]["fname"].value;
      var lname = document.forms["s_search"]["lname"].value;
      console.log(!has_no_nums(fname));
      console.log(fname);
      console.log(fname.length);
      if (has_no_nums(fname) && fname && Array.from(fname).length != 0) {
        alert("First Name: First name can't have numbers");
        return false;
      }
      else if (has_no_nums(lname) && Array.from(lname).length != 0) {
        alert("Last Name: Last name can't have numbers");
        return false;
      }
    }
    function has_no_nums(s) {
      return /\d/.test(s);
    }

    function validateSemester() {
      var s = document.forms["sem"]["sem_no"].value;
      console.log(s)
      if (s == '' || isNaN(s)) {
        alert("Please enter a semester number for 0 to 3");
        return false;
      }
    }