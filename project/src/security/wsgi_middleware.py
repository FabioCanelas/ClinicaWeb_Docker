"""
Middleware WSGI para manejo avanzado de headers de seguridad
Intercepta y modifica headers a nivel WSGI, incluyendo el header Server
"""

class SecurityHeadersMiddleware:
    """
    Middleware WSGI que gestiona headers de seguridad a bajo nivel
    Soluciona el problema del header Server en desarrollo
    """
    
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        """
        Intercepta la respuesta y modifica headers de seguridad
        """
        def new_start_response(status, response_headers, exc_info=None):
            """
            Wrapper de start_response que modifica headers
            """
            # Convertir headers a lista modificable y filtrar headers problemáticos
            headers = []
            
            for name, value in response_headers:
                # Omitir headers que exponen información sensible
                if name.lower() not in ['server', 'x-powered-by', 'x-generator']:
                    headers.append((name, value))
                elif name.lower() == 'server':
                    # 🔒 TC17: Si hay header Server, verificar si contiene información sensible
                    # En algunos casos, headers múltiples se combinan con comas
                    if any(tech in value.lower() for tech in ['werkzeug', 'python', 'flask', 'gunicorn']):
                        # Reemplazar completamente con valor seguro
                        continue  # Omitir este header, lo agregaremos limpio
                    else:
                        # Mantener si ya es seguro
                        headers.append((name, value))
            
            # 🔒 TC17: Agregar header Server genérico y seguro (siempre)
            headers.append(('Server', 'nginx'))
            
            return start_response(status, headers, exc_info)
        
        return self.app(environ, new_start_response)
