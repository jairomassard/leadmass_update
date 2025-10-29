# Instrucciones para la actualización de la base de datos

Este proyecto incluye una nueva funcionalidad para registrar el **precio de venta** asociado a cada lead. Para soportar este cambio se agregó una nueva columna llamada `precio_venta` en la tabla `leads` de la base de datos PostgreSQL. La mayoría de las consultas y actualizaciones del backend han sido modificadas para leer y escribir este valor cuando esté disponible.

Para aplicar este cambio en su instancia de base de datos existente ejecute la siguiente sentencia SQL:

```sql
ALTER TABLE leads ADD COLUMN precio_venta NUMERIC NULL;
```

Esta instrucción añadirá la columna con capacidad para valores numéricos y permitirá valores nulos en caso de que el precio aún no se haya definido.  Después de crear la columna, no es necesario modificar los datos existentes; todos los campos tendrán valor `NULL` hasta que se actualicen desde la aplicación.

**Nota:** si utiliza un motor diferente o un tipo de dato distinto para almacenar precios, ajuste el tipo `NUMERIC` según sus necesidades (por ejemplo `DECIMAL(12,2)` para limitar la precisión y escala).