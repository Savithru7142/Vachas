document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('mobile-menu-toggle');
  const menu = document.getElementById('mobile-nav');
  const body = document.body;

  if (toggle && menu) {
    toggle.addEventListener('click', () => {
      const isOpen = menu.classList.toggle('hidden');
      body.classList.toggle('mobile-menu-open', !isOpen);
      toggle.setAttribute('aria-expanded', String(!isOpen));
    });
  }

  document.querySelectorAll('[data-dismiss="alert"]').forEach((btn) => {
    btn.addEventListener('click', () => {
      btn.closest('.v-alert')?.remove();
    });
  });

  const modalTriggers = document.querySelectorAll('[data-modal-target]');
  modalTriggers.forEach((trigger) => {
    trigger.addEventListener('click', () => {
      const target = document.getElementById(trigger.dataset.modalTarget);
      target?.classList.remove('hidden');
    });
  });

  document.querySelectorAll('[data-modal-close]').forEach((btn) => {
    btn.addEventListener('click', () => {
      btn.closest('[data-modal]')?.classList.add('hidden');
    });
  });

  const dashToggle = document.getElementById('dashboard-menu-toggle');
  const dashSidebar = document.getElementById('dashboard-sidebar');
  if (dashToggle && dashSidebar) {
    dashToggle.addEventListener('click', () => {
      dashSidebar.classList.toggle('hidden');
      dashSidebar.classList.toggle('fixed');
      dashSidebar.classList.toggle('inset-y-0');
      dashSidebar.classList.toggle('left-0');
      dashSidebar.classList.toggle('z-40');
      dashSidebar.classList.toggle('shadow-lg');
    });
  }
});
