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

async function submitForm(event) {
  event.preventDefault();

  const form = document.getElementById('ymk-form');
  const formData = new FormData(form);

  // Format birthday
  const year = formData.get('Year');
  const month = formData.get('Month');
  const day = formData.get('Day').padStart(2, '0');
  formData.set('birthday', `${year}/${month}/${day}`);

  // Handle submit button UI
  const submitButton = document.querySelector("input[type='submit']");
  submitButton.disabled = true;
  submitButton.value = "Loading...";

  // Handle mission_paper (file) input
  const fileInput = document.getElementById("mission_paper");
  if (fileInput.files.length > 0) {
    const file = fileInput.files[0];

    // Check file size
    if (file.size > 1024 * 1024 * 2) {
      alert("Error: 파일 크기는 2MB를 초과할 수 없습니다.");
      submitButton.disabled = false;
      submitButton.value = "Submit";
      return;
    }

    const reader = new FileReader();
    reader.onload = async function () {
      const base64 = reader.result.split(",")[1]; // remove data:image/...;base64,
      formData.append("mission_paper_base64", base64); // send as base64

      // Now submit with base64 included
      await sendForm(formData);
    };
    reader.readAsDataURL(file);
  } else {
    // No file, just submit
    await sendForm(formData);
  }

  // Helper function to submit
  async function sendForm(formData) {
    try {
      const response = await fetch(
        'https://script.google.com/macros/s/AKfycbyrtg0CKGN0oZA21KrlIt3jko3kkT2lFhKfXf4fHVumOmpJrLdOKuexh6Sje3Xlnz8YTg/exec',
        {
          method: 'POST',
          body: formData,
        }
      );
      const data = await response.json();

      if (data.status === 'success') {
        document.getElementById('success-message').style.display = 'block';
        form.reset();
        setTimeout(() => {
          document.getElementById('success-message').style.display = 'none';
        }, 3000);
      } else {
        throw new Error('Submission failed');
      }
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      submitButton.disabled = false;
      submitButton.value = "Submit";
    }
  }
}

