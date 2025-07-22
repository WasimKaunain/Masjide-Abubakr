async function sendOTP() {
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
   window.location.href = '/cash-form';
  }
}
  


async function submitCashForm() {
  const donorName = document.getElementById("donor-name").value;
  const amount = document.getElementById("donation-amount").value;
  const treasurer = document.getElementById("treasurer-name").value;

  if (!donorName || !amount || !treasurer) {
    alert("Please fill in all fields.");
    return;
  }

  // Store donor name locally if needed later
  localStorage.setItem("donorName", donorName);

  alert("Form submitted successfully!"); // Replace with actual logic
}
