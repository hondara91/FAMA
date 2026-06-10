# Manual de Usuario - FAMA
## Foro de Apoyo Multipropósito de la Armada

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Guía de Inicio](#guía-de-inicio)
3. [Funcionalidades por Rol](#funcionalidades-por-rol)
4. [Módulos de la Aplicación](#módulos-de-la-aplicación)
5. [Perfil de Usuario](#perfil-de-usuario)
6. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## Introducción

**FAMA** es una plataforma web comunitaria diseñada específicamente para el personal de la Armada. La aplicación facilita la comunicación, colaboración e intercambio de información en cuatro áreas principales:

- **Viviendas**: Alquiler, intercambio y compartir vivienda
- **Servicios**: Oferta y demanda de servicios diversos
- **Compra-Venta**: Intercambio de artículos entre usuarios
- **Ocio y Eventos**: Organización de actividades y eventos
- **Foro**: Debates y conversación comunitaria

La plataforma cuenta con un sistema de roles que permite diferentes niveles de acceso y responsabilidades según tu perfil.

---

## Guía de Inicio

### Acceso a la aplicación

1. Abre tu navegador en la URL del servidor donde está desplegada la aplicación.
2. Si el servidor utiliza Nginx con certificados, accede mediante **HTTPS**.
3. No es necesario indicar un puerto si el dominio está configurado en los puertos estándar **80** (HTTP) o **443** (HTTPS).

### Registro

1. Accede a la aplicación desde tu navegador
2. Haz clic en **"Registro"** en la página de inicio
3. Completa el formulario con:
   - **ID de usuario**: Identificador único para la plataforma (sin espacios)
   - **Nombre**: Tu nombre
   - **Apellidos**: Tus apellidos
   - **Email**: Tu correo electrónico (será tu método de identificación principal)
   - **Contraseña**: Mínimo 8 caracteres (usa mayúsculas, minúsculas, números y símbolos para mayor seguridad)
   - **Pregunta de seguridad**: Selecciona una pregunta y proporciona la respuesta (para recuperación de cuenta)
4. Haz clic en **"Registrarse"**

**Nota**: Tu cuenta requiere validación por parte de un administrador antes de poder acceder completamente.

### Inicio de Sesión

1. Ve a la página de login de la aplicación
2. Ingresa tu **ID de usuario** y **contraseña**
3. Haz clic en **"Iniciar Sesión"**

Si has olvidado tu contraseña:
- Haz clic en **"¿Olvidaste tu contraseña?"**
- Responde tu pregunta de seguridad
- Se te generará una nueva contraseña temporal

### Cambio de Contraseña

Para cambiar tu contraseña:
1. Una vez logueado, ve a tu **Perfil**
2. Haz clic en **"Cambiar Contraseña"**
3. Introduce tu contraseña actual
4. Introduce tu nueva contraseña
5. Confirma la nueva contraseña
6. Haz clic en **"Guardar Cambios"**

---

## Funcionalidades por Rol

### 👤 Usuario Regular

**Descripción**: Rol por defecto para todos los nuevos registros. Permite acceder a todos los módulos de la aplicación.

**Permisos**:
- ✓ Ver anuncios en todos los módulos
- ✓ Crear anuncios propios
- ✓ Editar sus propios anuncios
- ✓ Eliminar sus propios anuncios
- ✓ Participar en el foro
- ✓ Ver eventos y actividades de ocio
- ✓ Gestionar su perfil personal
- ✓ Subir foto de perfil
- ✓ Ver información de otros usuarios

**Funcionalidades principales**:
1. Crear y gestionar anuncios de vivienda
2. Ofrecer o buscar servicios
3. Publicar artículos para compraventa
4. Organizar o participar en eventos
5. Participar en discusiones del foro
6. Consultar novedades de la plataforma

---

### 👨‍💼 Gestor

**Descripción**: Rol intermedio con responsabilidades de moderación y gestión de contenidos.

**Permisos adicionales a Usuario**:
- ✓ Acceder al panel de gestión
- ✓ Ver lista de todos los usuarios
- ✓ Ver detalles de usuarios individuales
- ✓ Editar información de otros usuarios (nombre real, apellidos, email)
- ✓ Resetear contraseñas de usuarios
- ✓ Moderar contenidos (eliminación de anuncios inapropiados)
- ✓ Ver estadísticas generales de la plataforma
- ✓ Acceder a algunos logs de actividad

**Funcionalidades del Panel de Gestión**:

#### Panel Principal
- Visualización de estadísticas globales
- Usuarios activos validados
- Anuncios pendientes de revisión
- Accesos rápidos a secciones administrativas

#### Gestión de Usuarios
- **Ver usuarios**: Lista completa con estado de validación
- **Buscar usuarios**: Por nombre o email
- **Editar usuario**: Actualizar información personal
- **Resetear contraseña**: Generar contraseña temporal
- **Ver detalles**: Información completa del perfil

#### Moderación
- Revisión de anuncios denunciados
- Eliminación de contenido inapropiado
- Advertencias a usuarios (si aplica)

---

### 👨‍💻 Administrador

**Descripción**: Rol de máximo nivel con control total sobre la plataforma.

**Permisos adicionales a Gestor**:
- ✓ Cambiar rol de usuarios (usuario ↔ gestor ↔ admin)
- ✓ Eliminar usuarios completamente
- ✓ Ver, filtrar y exportar logs completos
- ✓ Eliminar logs de la base de datos
- ✓ Acceso a todos los controles de administración
- ✓ Gestión completa de la plataforma

**Funcionalidades del Panel de Administración**:

#### Gestión Completa de Usuarios
- Cambiar roles de usuarios
- Eliminar usuarios (con confirmación)
- Gestión de activaciones/desactivaciones
- Control total de permisos

#### Sistema de Logs
- Ver historial completo de actividades
- Filtrar por tipo de acción, usuario o fecha
- Exportar logs en PDF para auditoría
- Eliminar registros de logs

#### Estadísticas Avanzadas
- Análisis detallado de uso de plataforma
- Reportes de actividad
- Métricas de rendimiento

---

## Módulos de la Aplicación

### 🏠 Viviendas

**Objetivo**: Facilitar el alquiler, intercambio y compartición de viviendas entre usuarios.

#### Tipos de Oferta
- **Alquiler**: Buscar o ofrecer vivienda en alquiler
- **Intercambio**: Intercambiar vivienda de forma temporal
- **Compartir**: Buscar compañero de piso o compartir gastos

#### Información de la Vivienda
Cuando creas o buscas una vivienda, encontrarás:
- **Tipo de inmueble**: Piso, estudio, chalet, ático, finca
- **Ubicación**: Ciudad y zona/barrio específico
- **Características**:
  - Número de habitaciones
  - Número de baños
  - Planta en la que se encuentra
- **Precio**: Precio mensual de alquiler (cuando aplique)
- **Extras**: Garaje, ascensor, permitidas mascotas, etc.
- **Datos de contacto**: Teléfono del propietario/interesado
- **Descripción**: Detalles adicionales y características especiales
- **Fotos**: Imágenes del inmueble
- **Validez**: El anuncio expirará automáticamente tras un período

#### Acciones Disponibles
- Ver listado de todas las viviendas
- Ver detalles de una vivienda específica
- Crear un nuevo anuncio de vivienda
- Editar tus propios anuncios
- Eliminar tus anuncios
- Contactar al propietario por teléfono
- Guardar anuncios favoritos

---

### 💼 Servicios

**Objetivo**: Facilitar la oferta y búsqueda de servicios entre usuarios.

#### Tipos de Servicios
- **Viajes compartidos**: Compartir viaje con otros usuarios
- **Clases de apoyo**: Ofrecer o buscar tutorías
- **Trabajos**: Ofrecer servicios puntuales o buscar ayuda

#### Información del Servicio
- **Tipo**: Ofrecer o buscar
- **Categoría**: Clasificación del servicio
- **Título**: Descripción breve del servicio
- **Precio**: Coste del servicio (si aplica)
- **Modalidad**: Presencial u online
- **Teléfono**: Contacto directo
- **Ciudad**: Ubicación del servicio
- **Descripción**: Detalles completos
- **Fotos**: Imágenes relevantes (cuando sea apropiado)

#### Acciones Disponibles
- Navegar por categorías de servicios
- Ver detalles de servicios disponibles
- Crear anuncio de servicio nuevo
- Editar tus anuncios de servicio
- Eliminar anuncios propios
- Contactar al oferente

---

### 🛍️ Compra-Venta

**Objetivo**: Facilitar el comercio de artículos entre usuarios.

#### Información del Artículo
- **Nombre del artículo**: Descripción breve
- **Categoría**: Clasificación (electrónica, mobiliario, etc.)
- **Precio**: Valor del artículo
- **Descripción**: Detalles, condición del artículo, etc.
- **Fotos**: Imágenes del producto (máximo 5)
- **Contacto**: Teléfono o email del vendedor
- **Ubicación**: Ciudad donde se entrega/recoge

#### Estados del Anuncio
- **Activo**: Disponible para comprar
- **Vendido**: Artículo ya ha sido vendido
- **Pausado**: Temporalmente no disponible

#### Acciones Disponibles
- Ver listado de artículos disponibles
- Filtrar por categoría o precio
- Ver detalles y fotos del artículo
- Publicar un artículo para vender
- Editar tus anuncios
- Eliminar anuncios
- Marcar como vendido
- Contactar al vendedor

---

### 🎉 Ocio y Eventos

**Objetivo**: Facilitar la organización y participación en actividades recreativas y eventos.

#### Tipos de Eventos
- Actividades deportivas
- Eventos sociales
- Actividades culturales
- Reuniones de compañerismo
- Excursiones y viajes

#### Información del Evento
- **Nombre del evento**: Título descriptivo
- **Fecha y hora**: Cuándo se realiza
- **Ubicación**: Lugar del evento
- **Descripción**: Detalles del evento
- **Aforo**: Número máximo de participantes
- **Coste**: Si hay entrada (opcional)
- **Contacto**: Organizador
- **Inscripción**: Formulario o información para participar

#### Acciones Disponibles
- Ver calendario de eventos
- Ver detalles de eventos próximos
- Crear un nuevo evento
- Editar tus eventos
- Ver inscritos en tus eventos
- Inscribirse en un evento
- Cancelar inscripción
- Contactar al organizador

---

### 💬 Foro

**Objetivo**: Facilitar discusiones comunitarias en temas de interés común.

#### Estructura del Foro
- **Canales**: Temas principales de discusión
  - Canal General: Temas de interés general
  - Consultas técnicas: Dudas sobre la plataforma
  - Sugerencias: Propuestas de mejora
  - Social: Temas sociales y de compañerismo
  - Otros (según sea necesario)

#### Funcionalidades
- **Ver canales**: Lista de todos los canales disponibles
- **Leer conversaciones**: Acceder a todos los mensajes de un canal
- **Crear conversación**: Iniciar nuevo hilo de discusión
- **Responder**: Comentar en una conversación
- **Editar posts**: Modificar tus propios mensajes
- **Eliminar posts**: Borrar tus mensajes (si aplica)

#### Normas del Foro
- Sé respetuoso con otros usuarios
- No publiques spam o contenido ofensivo
- Usa un lenguaje apropiado
- No compartas información personal de otros
- Reporta contenido inapropiado

---

### 📰 Novedades

**Objetivo**: Consultar noticias y actualizaciones importantes de la plataforma.

#### Contenido
- Anuncios de la plataforma
- Cambios y mejoras
- Eventos especiales
- Avisos importantes

#### Acciones Disponibles
- Ver listado de novedades recientes
- Leer detalles de una novedad
- Filtrar por fecha
- Compartir noticias (si aplica)

---

## Perfil de Usuario

### Edición del Perfil

Accede a **Perfil** en el menú principal para gestionar tu información:

#### Información Personal
- **Nombre real**: Tu nombre completo
- **Apellidos**: Tus apellidos
- **Email**: Tu correo (no se puede cambiar)
- **Nombre de usuario**: Tu identificador único

#### Foto de Perfil
- Haz clic en **"Cambiar foto de perfil"**
- Selecciona una imagen de tu dispositivo (PNG, JPG, JPEG, GIF, WEBP)
- La imagen se redimensionará automáticamente
- Haz clic en **"Guardar"**

#### Seguridad
- **Cambiar contraseña**: Actualiza tu contraseña regularmente
- **Pregunta de seguridad**: Mantén actualizada para recuperación de cuenta

#### Información Adicional
- Visualización de tu información pública
- Estadísticas de actividad
- Historial de anuncios (según tu rol)

---

## Preguntas Frecuentes

### 🔑 Autenticación y Cuenta

**P: ¿Cuál es el requisito mínimo para la contraseña?**
R: La contraseña debe tener mínimo 8 caracteres. Se recomienda usar mayúsculas, minúsculas, números y símbolos para mayor seguridad.

**P: ¿Qué hago si olvido mi contraseña?**
R: En la página de login, haz clic en "¿Olvidaste tu contraseña?" y responde tu pregunta de seguridad. Se te generará una nueva contraseña temporal.

**P: ¿Mi cuenta es activada inmediatamente al registrarse?**
R: No, tu cuenta debe ser validada por un administrador antes de tener acceso completo. Recibirás un email de confirmación.

**P: ¿Puedo cambiar mi email?**
R: No, el email es tu identificador único y no se puede cambiar. Si necesitas cambiar de email, contacta con un administrador.

**P: ¿Necesito un puerto específico para acceder a la aplicación?**
R: Si el servidor está configurado con Nginx en los puertos estándar, basta con usar el dominio o la IP. No es necesario indicar un puerto extra en la URL.

---

### 📋 Módulos y Anuncios

**P: ¿Cuánto tiempo permanece activo mi anuncio?**
R: Los anuncios permanecen activos durante un período determinado y después expiran automáticamente. Revisa la fecha de expiración en tus anuncios.

**P: ¿Puedo editar un anuncio después de publicarlo?**
R: Sí, puedes editar tus propios anuncios mientras estén activos. Solo haz clic en "Editar" en el anuncio.

**P: ¿Cómo elimino un anuncio?**
R: Ve a tu anuncio y haz clic en "Eliminar". Confirma la eliminación en el diálogo de confirmación.

**P: ¿Cuántas fotos puedo subir en un anuncio?**
R: Depende del módulo, pero generalmente se permiten múltiples fotos. Verifica los límites en cada módulo.

**P: ¿Puedo subir videos?**
R: Actualmente la plataforma soporta principalmente imágenes. Los videos no se pueden subir directamente.

---

### 👥 Perfiles y Contacto

**P: ¿Cómo contacto con otro usuario?**
R: En los detalles de cada anuncio aparecerá un teléfono o información de contacto del usuario. Úsala para comunicarte.

**P: ¿Puedo ver la información de otros usuarios?**
R: Sí, puedes ver la información pública del perfil de otros usuarios, incluyendo su nombre y foto.

**P: ¿Cómo cambio mi foto de perfil?**
R: Ve a tu Perfil y haz clic en "Cambiar foto de perfil". Selecciona una imagen de tu dispositivo.

---

### 🛡️ Seguridad y Privacidad

**P: ¿Es segura mi información personal?**
R: Usamos sistemas de encriptación estándar para proteger tu información. Las contraseñas se almacenan con hash seguro (PBKDF2).

**P: ¿Quién puede ver mis datos personales?**
R: Los administradores y gestores pueden ver tu información con fines de gestión de plataforma. Tu información básica es visible para otros usuarios.

**P: ¿Cómo reporto contenido inapropiado?**
R: Contacta con un administrador o gestor indicando el anuncio o contenido problemático.

**P: ¿Puedo cambiar mi rol de usuario?**
R: No directamente. Un administrador puede cambiar tu rol si lo considera necesario. Contacta con ellos.

---

### 🆘 Soporte Técnico

**P: ¿Qué hago si encuentro un error?**
R: Toma nota del error (incluyendo la URL donde ocurrió) y contacta con un administrador proporcionando detalles.

**P: ¿La plataforma está disponible 24/7?**
R: La plataforma debe estar disponible continuamente, aunque puede tener mantenimiento programado. Se avisará con anticipación.

**P: ¿En qué navegadores funciona FAMA?**
R: FAMA funciona en todos los navegadores modernos (Chrome, Firefox, Safari, Edge).

**P: ¿Funciona en dispositivos móviles?**
R: Sí, FAMA está optimizada para dispositivos móviles y tablets.

---

## Resumen de Accesos por Rol

| Función | Usuario | Gestor | Admin |
|---------|---------|--------|-------|
| **Crear anuncios** | ✓ | ✓ | ✓ |
| **Editar propios anuncios** | ✓ | ✓ | ✓ |
| **Ver panel de gestión** | ✗ | ✓ | ✓ |
| **Gestionar otros usuarios** | ✗ | ✓ | ✓ |
| **Cambiar roles** | ✗ | ✗ | ✓ |
| **Eliminar usuarios** | ✗ | ✗ | ✓ |
| **Ver y exportar logs** | ✗ | Parcial | ✓ |
| **Acceder a estadísticas** | ✗ | ✓ | ✓ |
| **Moderación de contenidos** | ✗ | ✓ | ✓ |

---

## Contacto y Soporte

Para más información, dudas o reportar problemas, contacta con:
- **Administrador de la plataforma**: Disponible en el panel de admin
- **Equipo técnico**: Consulta el formulario de contacto en la plataforma

---

**Última actualización**: Junio de 2026

*Manual de usuario de FAMA - Foro de Apoyo Multipropósito de la Armada*
