document.getElementById("logoimg").onclick = function() {
    alert("Welcome to YMK.com!");
}

let clickCount = 0;

function ChangeText(){
    let text = document.getElementById("prank");
    text.innerHTML = "You got fooled";
    text.style.fontSize = "40px";
    text.style.fontFamily = "Comic Sans Ms";
    text.style.color = "pink";
    if (clickCount == 1){
        text.innerHTML = "To Get Free Money, Click the Button!";
        text.style.fontSize = "16px";
        text.style.fontFamily = "serif";
        text.style.color = "black";
        clickCount=0;
    }
    else{
        clickCount=1;
    }
}

function submitForm(event) {
  event.preventDefault();

  const form = document.getElementById('ymk-form');
  const formData = new FormData(form);

  const year = formData.get('Year');
  const month = formData.get('Month');
  const day = formData.get('Day').padStart(2, '0');
  formData.set('birthday', `${year}/${month}/${day}`);

  // Don't convert to URLSearchParams and don't set headers manually
  fetch('https://script.google.com/macros/s/AKfycbxnjnOCwPVm5inBd-mOjsR3HfBnQmbvyC3mkhlo3ic9sQJPEN-nNfHJlzlHX7mKm2FfaA/exec', {
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      document.getElementById('success-message').style.display = 'block';
      form.reset();
      setTimeout(() => {
        document.getElementById('success-message').style.display = 'none';
      }, 3000);
    } else {
      throw new Error('Submission failed');
    }
  })
  .catch(error => {
    alert('Error: ' + error.message);
  });
}
