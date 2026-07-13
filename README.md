# Aplicacion web Store26

Aplicacion web en Python con Flask y MySQL/MariaDB para gestionar clientes, vendedores, productos, pedidos, detalle de pedidos e informe de pedidos.

## 1. Requisitos

- XAMPP instalado.
- Python 3.10 o superior.
- Navegador web.

## 2. Encender MySQL en XAMPP

1. Abra el panel de control de XAMPP.
2. Presione **Start** en el modulo **MySQL**.
3. Confirme que MySQL quede en color verde.
4. Presione **Admin** en MySQL para abrir phpMyAdmin.

## 3. Crear la base de datos `store26`

Opcion recomendada con phpMyAdmin:

1. Entre a `http://localhost/phpmyadmin`.
2. Abra la pestana **SQL**.
3. Copie y ejecute el contenido del archivo:

   `database/store26.sql`

Ese archivo crea:

- Base de datos `store26`.
- Tabla `clientes`.
- Tabla `vendedores`.
- Tabla `productos`.
- Tabla `pedidos`.
- Tabla `pedido_detalles`.
- Registros demo para probar rapidamente.

## 4. Crear el entorno virtual llamado `store`

Abra una terminal dentro de la carpeta del proyecto y ejecute:

```powershell
python -m venv store
```

Active el entorno virtual:

```powershell
.\store\Scripts\Activate.ps1
```

Si PowerShell bloquea la activacion, ejecute una sola vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Luego vuelva a activar:

```powershell
.\store\Scripts\Activate.ps1
```

## 5. Instalar dependencias

Con el entorno virtual activo:

```powershell
pip install -r requirements.txt
```

## 6. Configurar conexion a XAMPP

1. Copie el archivo `.env.example`.
2. Pegue la copia con el nombre `.env`.
3. Para una instalacion normal de XAMPP, deje estos valores:

```env
FLASK_SECRET_KEY=store26-dev-key
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=store26
```

Si su usuario root de MySQL tiene contrasena, escribala en `MYSQL_PASSWORD`.

## 7. Ejecutar la aplicacion

Con MySQL encendido en XAMPP y el entorno virtual activo:

```powershell
python run.py
```

Abra en el navegador:

```text
http://127.0.0.1:5000
```

## 8. Estructura de archivos

```text
store26_app/
  app/
    static/
      styles.css
    templates/
      base.html
      index.html
      clientes.html
      cliente_form.html
      vendedores.html
      vendedor_form.html
      productos.html
      producto_form.html
      pedidos.html
      pedido_form.html
      pedido_ver.html
      informe_pedidos.html
      _tabla_pedidos.html
    __init__.py
    db.py
    routes.py
  database/
    store26.sql
  .env.example
  requirements.txt
  run.py
  README.md
```

## 9. Operaciones disponibles

- Clientes: crear, listar, editar y eliminar.
- Vendedores: crear, listar, editar y eliminar.
- Productos: crear, listar, editar y eliminar.
- Pedidos: crear, listar, ver detalle, editar y eliminar.
- Informe de pedidos: filtrar por fecha inicial, fecha final y estado; imprimir desde el navegador.

## 10. Orden recomendado de uso

1. Registrar clientes.
2. Registrar vendedores.
3. Registrar productos.
4. Registrar pedidos seleccionando cliente, vendedor y productos.
5. Revisar el informe de pedidos.

## 11. Nota importante sobre eliminaciones

La base de datos protege la integridad de la informacion:

- No permite eliminar un cliente o vendedor si ya tiene pedidos.
- No permite eliminar un producto si aparece en pedidos.
- Al eliminar un pedido, se eliminan automaticamente sus detalles.
