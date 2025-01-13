// Función para Mostrar Notificaciones
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Mostrar con animación de entrada
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);

    // Desaparecer después de 5 segundos
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, 5000);
}

// Confirmación Personalizada para Resetear
document.querySelector('.reset-button').addEventListener('click', function(event) {
    event.preventDefault();

    // Crear Modal de Confirmación Personalizada
    const modal = document.createElement('div');
    modal.className = 'custom-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>¿Estás seguro de que deseas limpiar y resetear?</h3>
            <div class="modal-buttons">
                <button class="confirm">Confirmar</button>
                <button class="cancel">Cancelar</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Acción de Confirmar
    modal.querySelector('.confirm').addEventListener('click', () => {
        window.location.href = '/reset/';
        showNotification('Los datos fueron reseteados correctamente.', 'success');
        modal.remove();
    });

    // Acción de Cancelar
    modal.querySelector('.cancel').addEventListener('click', () => {
        showNotification('Operación cancelada.', 'warning');
        modal.remove();
    });
});

/* Estilización de Notificaciones */
const style = document.createElement('style');
style.innerHTML = `
    /* Estilo de Notificaciones */
    .notification {
        position: fixed;
        top: -50px;
        right: 20px;
        background-color: #4caf50;
        color: white;
        padding: 15px 30px;
        border-radius: 5px;
        font-size: 1em;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        opacity: 0;
        transform: translateY(-20px);
        transition: all 0.5s ease;
        z-index: 1000;
    }

    .notification.show {
        top: 20px;
        opacity: 1;
        transform: translateY(0);
    }

    .notification.error {
        background-color: #d9534f;
    }

    .notification.warning {
        background-color: #f0ad4e;
    }

    /* Modal Personalizado */
    .custom-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1050;
    }

    .modal-content {
        background-color: white;
        padding: 30px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
        animation: fadeIn 0.3s ease;
    }

    .modal-buttons {
        margin-top: 20px;
    }

    .modal-buttons button {
        padding: 12px 30px;
        margin: 0 10px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 1em;
        transition: background-color 0.3s ease;
    }

    .modal-buttons .confirm {
        background-color: #2c7d59;
        color: white;
    }

    .modal-buttons .cancel {
        background-color: #d9534f;
        color: white;
    }

    .modal-buttons button:hover {
        opacity: 0.9;
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: scale(0.95);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
`;
document.head.appendChild(style);
