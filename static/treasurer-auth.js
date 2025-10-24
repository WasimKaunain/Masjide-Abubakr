async function sendOTP() {
  const sendOtpButton = document.getElementById("send-otp-button");
  const spinner = document.getElementById("spinner");

  // Disable button and show spinner
  sendOtpButton.disabled = true;
  spinner.style.display = "inline-block";

  const email = document.getElementById("email").value;

  try {
    const response = await fetch('/send-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });

    const contentType = response.headers.get("content-type");
    const result = contentType && contentType.includes("application/json") 
      ? await response.json() 
      : { message: "Unexpected server response" };

    alert(result.message);

    if (response.ok) {
      document.getElementById('otp-section').style.display = 'block';
    }
  } catch (error) {
    console.error("Error sending OTP:", error);
    alert("Failed to send OTP. Please try again.");
  } finally {
    // ✅ Always executed (success or error)
    spinner.style.display = "none";   // hide spinner
    sendOtpButton.disabled = false;   // enable button again
  }
}



async function verifyOTP() {
  const otp = document.getElementById("otp").value;   

  if (!otp) {
    alert("Please enter the OTP.");
    return;
  }

  const response = await fetch('/verify-otp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ otp })
  });

  const result = await response.json(); 
  alert(result.message);

  if (response.ok) {
    // Show the next form or redirect
  window.location.href = '/treasurer-dashboard';
  }
}
  


async function submitSalaryForm() {
  const spinner = document.getElementById("spinner");
  const submitBtn = document.getElementById("submit-button")
  // Disable button and show spinner
  submitBtn.disabled = true;
  spinner.style.display = "inline-block";

  const payerName = document.getElementById("salary-payer-name").value;
  const amount = document.getElementById("salary-amount").value;
  const date = document.getElementById("date").value;

  if (!payerName || !amount || !date) {
    alert("Please fill in all fields.");
    return;
  }

  try {
        const response = await fetch('/pay-salary', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({  payerName : payerName,
                                                                                                                                            amount : amount,
                                                                                                                                            date : date
                                                                                                                                          }
                                                                                                                                        )
                                                    }
                                    );
          if(response.ok) 
            {
              const result = await response.json();
              alert(result.message || "Form submitted successfully!"); 
              window.location.href = '/';
            } 
          else 
            {
            alert("Failed to submit form");
            resetSubmitButton();
            };

      } 
  catch (error) 
      {
        console.error("Error : ",error);
        alert("Error submitting form");
        resetSubmitButton();
      } 
  
}

function resetSubmitButton() {
  submitBtn.disabled = false;
  spinner.style.display = "none";
}
