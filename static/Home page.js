async function submitForm(event) {
  event.preventDefault();

  const form = document.getElementById('ymk-form');
  const formData = new FormData(form);

  // Format and add birthday
  const year = formData.get('Year');
  const month = formData.get('Month');
  const day = formData.get('Day');

  if (year && month && day) {
    const formattedDay = day.padStart(2, '0');
    formData.append('birthday', `${year}/${month}/${formattedDay}`);
  }

  // UI: Disable submit button
  const submitButton = document.querySelector("input[type='submit']");
  submitButton.disabled = true;
  submitButton.value = "Loading...";

  // Handle mission_paper (file) input
  const fileInput = document.getElementById("mission_paper");
  if (fileInput && fileInput.files.length > 0) {
    const file = fileInput.files[0];

    if (file.size > 5 * 1024 * 1024) {  // 5MB limit
      alert("Error: 파일 크기는 5MB를 초과할 수 없습니다.");
      submitButton.disabled = false;
      submitButton.value = "Submit";
      return;
    }

    const reader = new FileReader();
    reader.onload = async function () {
      const base64 = reader.result.split(",")[1]; // Remove "data:*/*;base64,"
      formData.append("mission_paper_base64", base64);

      await sendForm(formData, submitButton, form);
    };
    reader.readAsDataURL(file);
  } else {
    await sendForm(formData, submitButton, form);
  }
}

// Helper function to send form
async function sendForm(formData, submitButton, form) {
  try {
    const response = await fetch(
      'https://script.google.com/macros/s/AKfycbxkRWXqrjNXBHDXwHlwm1sTOzNMBpKXNI3-IFo-ahtNmN-_0u-zJPC18Ddg0kD7Mr5NYQ/exec',
      {
        method: 'POST',
        body: formData,
      }
    );

    const data = await response.json();

    if (data.status === 'success') {
      alert("성공적으로 제출되었습니다. 감사합니다!");
      form.reset();
    } else {
      throw new Error(data.message || 'Submission failed');
    }
  } catch (error) {
    alert('제출 중 오류 발생: ' + error.message);
  } finally {
    submitButton.disabled = false;
    submitButton.value = "Submit";
  }
}
