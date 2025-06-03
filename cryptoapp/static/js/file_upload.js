document.getElementById('openUploadBtn').addEventListener('click', () => {
    const modal = new bootstrap.Modal(document.getElementById('uploadModal'));
    modal.show();
  });
  
  document.getElementById('uploadForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(this);
  
    fetch('/files/upload/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
      },
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        location.reload();  // or dynamically insert into DOM
      } else {
        alert('Upload failed');
      }
    });
  });
  
  document.querySelectorAll('.encrypt-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const fileId = this.closest('.file-row').dataset.id;
      fetch(`/files/encrypt/${fileId}/`).then(() => location.reload());
    });
  });
  
  document.querySelectorAll('.decrypt-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const fileId = this.closest('.file-row').dataset.id;
      fetch(`/files/decrypt/${fileId}/`).then(() => location.reload());
    });
  });
  