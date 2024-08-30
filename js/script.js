function showPage(pageId) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => {
      if (page.id === pageId) {
        page.classList.remove('d-none');
      } else {
        page.classList.add('d-none');
      }
    });
  }
  
  // Initialize the app by showing the dashboard
  document.addEventListener('DOMContentLoaded', function () {
    showPage('dashboard');
  });
  
  const rangeInput = document.getElementById('customRange1');
    const rangeLabel = document.getElementById('rangeLabel');

    rangeInput.addEventListener('input', function() {
        const value = rangeInput.value;

        if (value == 0) {
            rangeLabel.textContent = `Belum Dikerjakan (${value}%)`;
        } else if (value > 0 && value < 50) {
            rangeLabel.textContent = `Masih dalam Proses (${value}%)`;
        } else if (value >= 50 && value < 100) {
            rangeLabel.textContent = `Sedang Dikerjakan (${value}%)`;
        } else if (value == 100) {
            rangeLabel.textContent = `Sudah Dikerjakan (${value}%)`;
        }
    });

    function handleOtherOption(selectElement) {
        const otherInputContainer = document.getElementById('otherInputContainer');
        if (selectElement.value === 'other') {
          otherInputContainer.classList.remove('d-none');
        } else {
          otherInputContainer.classList.add('d-none');
        }
      }

      $(document).ready(function() {
        $('#datetimepicker').flatpickr({
          enableTime: true,
          dateFormat: "Y-m-d H:i", // Format yang disimpan dalam input
          altInput: true,
          altFormat: "l, d F Y, H:i", // Format tampilan user
          time_24hr: true,
          locale: "id"
        });
      });