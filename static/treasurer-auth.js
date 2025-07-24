async function sendOTP() {
  const email = document.getElementById("email").value;

  try {
    const response = await fetch('/send-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });

    const contentType = response.headers.get("content-type");
    const result = contentType && contentType.includes("application/json") ? await response.json() : { message: "Unexpected server response" };

    alert(result.message);  // ✅ shows real message

    if (response.ok) {
      document.getElementById('otp-section').style.display = 'block';
    }
  } catch (error) {
    console.error("Error sending OTP:", error);
    alert("Failed to send OTP. Please try again.");
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
   document.getElementById("auth-section").style.display= 'none';
   
   document.getElementById("cash-form").style.display= 'block';
  }
}
  


async function submitCashForm() {
  const payerName = document.getElementById("salary-payer-name").value;
  const amount = document.getElementById("salary-amount").value;
  const date = document.getElementById("date").value;

  if (!payerName || !amount || !date) {
    alert("Please fill in all fields.");
    return;
  }

  try {
        const response = await fetch('/pay-salary', 
        { method: 'POST', 
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify(
            { payerName : payerName,
              amount : amount,
              date : date}
            )});
          if(response.ok) 
            {
              const result = await response.json();
              alert(result.message || "Form submitted successfully!"); 
              window.location.href = '/';
            } 
          else 
            {
            alert("Failed to submit form");
            };

      } 
      catch (error) 
      {
        console.error("Error : ",error);
        alert("Error submitting form");
      } 
  
}
