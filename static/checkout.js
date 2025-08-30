let upiId = "";

  // Fetch UPI ID from backend
  fetch("/config")
    .then(res => res.json())
    .then(data => {
      upiId = data.upiId;  // ✅ coming from env variable
    });

  // Show Pay Now button only when valid amount entered
  function togglePayButton() {
    const amount = document.getElementById("donationAmount").value;
    const payBtn = document.getElementById("pay-now-btn");

    if (amount && amount > 0) {
      payBtn.style.display = "inline-block";
    } else {
      payBtn.style.display = "none";
    }
  }

  // Handle payment redirection
  function goToPayment() {
    const amount = document.getElementById("donationAmount").value;

    if (amount > 0) {
      const name = encodeURIComponent("Mosque Donation");
      const url = `upi://pay?pa=${upiId}&pn=${name}&am=${amount}&cu=INR`;

      // Redirect to UPI app (mobile)
      window.location.href = url;
    } else {
      alert("Please enter a valid donation amount!");
    }
  }