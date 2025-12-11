import { useEffect } from 'react'

export default function Toast({ type = 'info', message, icon, onClose }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose()
    }, 4000)

    return () => clearTimeout(timer)
  }, [onClose])

  const typeConfig = {
    success: {
      bgColor: '#27ae60',
      textColor: '#27ae60',
      defaultIcon: '✓'
    },
    danger: {
      bgColor: '#e74c3c',
      textColor: '#e74c3c',
      defaultIcon: '✕'
    },
    error: {
      bgColor: '#e74c3c',
      textColor: '#e74c3c',
      defaultIcon: '✕'
    },
    warning: {
      bgColor: '#f39c12',
      textColor: '#f39c12',
      defaultIcon: '⚠'
    },
    info: {
      bgColor: '#17a2b8',
      textColor: '#17a2b8',
      defaultIcon: 'ℹ'
    }
  }

  const config = typeConfig[type] || typeConfig.info
  const displayIcon = icon || config.defaultIcon

  return (
    <div
      style={{
        position: 'fixed',
        top: '20px',
        right: '20px',
        zIndex: 9999,
        animation: 'slideIn 0.3s ease-out, fadeOut 0.3s ease-in 3.7s forwards'
      }}
    >
      <style>{`
        @keyframes slideIn {
          from {
            transform: translateX(400px);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        @keyframes fadeOut {
          from {
            opacity: 1;
          }
          to {
            opacity: 0;
          }
        }
      `}</style>
      
      <div
        style={{
          background: 'white',
          borderRadius: '8px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          padding: '16px 20px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          minWidth: '300px',
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        {/* Color bar left */}
        <div
          style={{
            position: 'absolute',
            left: 0,
            top: 0,
            bottom: 0,
            width: '4px',
            background: config.bgColor
          }}
        ></div>

        {/* Icon */}
        <div
          style={{
            fontSize: '24px',
            color: config.textColor,
            flexShrink: 0,
            fontWeight: 'bold'
          }}
        >
          {displayIcon}
        </div>

        {/* Message */}
        <div
          style={{
            flex: 1,
            marginLeft: '4px',
            color: '#34495e',
            fontWeight: '500',
            fontSize: '0.95rem'
          }}
        >
          {message}
        </div>

        {/* Close button */}
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            fontSize: '20px',
            cursor: 'pointer',
            color: '#95a5a6',
            padding: '0',
            flexShrink: 0,
            transition: 'color 0.2s'
          }}
          onMouseEnter={(e) => e.currentTarget.style.color = '#34495e'}
          onMouseLeave={(e) => e.currentTarget.style.color = '#95a5a6'}
        >
          ✕
        </button>
      </div>
    </div>
  )
}
