
let upiId = "";

fetch("/config")
  .then(res => res.json())
  .then(data => {
    upiId = data.upiId;  // ✅ coming from env variable
  });

function goToPayment() {
  if (selectedAmount > 0) {
    const upiId = "ansariw580@oksbi"; 
    const name = encodeURIComponent("Mosque Donation");
    const url = `upi://pay?pa=${upiId}&pn=${name}&am=${selectedAmount}&cu=INR`;

    // Open in same tab (works on mobile)
    window.location.href = url;

    // (Optional fallback for desktop)
    setTimeout(() => {
      alert("UPI apps are not supported on desktop. Please try from your mobile device.");
    }, 2000);
  } else {
    alert("Please select a donation amount first!");
  }

  
}
