async function updateProgressBar() 
{
  try {
    // Backend will return { current: 25000, target: 50000 }
    const res = await fetch('/get-current-total');
    const data = await res.json();
    
    const current = parseFloat(data.current) || 0;
    const target = parseFloat(data.target) || 0;

    // Calculate percentage
    const percent = target > 0 ? Math.min(100, (current / target) * 100) : 0;

    // Update progress bar
    document.getElementById("progress-fill").style.width = percent + "%";
    document.getElementById("progress-text").innerText =
      `₹${current.toFixed(2)} / ₹${target.toFixed(2)}`;

  } catch (err) {
    console.error("Error updating progress bar:", err);
  }
}
