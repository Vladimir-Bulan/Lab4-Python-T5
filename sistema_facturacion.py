import csv
from datetime import datetime

class Producto:
    def __init__(self, codigo, nombre, precio, tipo, cantidad):
        self.codigo = codigo
        self.nombre = nombre
        self.precio = precio
        self.tipo = tipo
        self.cantidad = cantidad

    @property
    def codigo(self):
        return self._codigo

    @codigo.setter
    def codigo(self, value):
        if len(value) == 4 and value.isdigit():
            self._codigo = value
        else:
            raise ValueError("El código debe tener 4 dígitos")

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, value):
        if 1 <= len(value) <= 100:
            self._nombre = value
        else:
            raise ValueError("El nombre debe tener entre 1 y 100 caracteres")

    @property
    def precio(self):
        return self._precio

    @precio.setter
    def precio(self, value):
        if 10 <= value <= 10000:
            self._precio = value
        else:
            raise ValueError("El precio debe estar entre 10 y 10000")

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, value):
        if 0 <= len(value) <= 20:
            self._tipo = value
        else:
            raise ValueError("El tipo debe tener entre 0 y 20 caracteres")

    @property
    def cantidad(self):
        return self._cantidad

    @cantidad.setter
    def cantidad(self, value):
        if 0 <= value <= 1000:
            self._cantidad = value
        else:
            raise ValueError("La cantidad debe estar entre 0 y 1000")

    def valorTotal(self):
        return self.precio * self.cantidad

class Oferta:
    def __init__(self, descripcion, codigos=[], tipos=[]):
        self.descripcion = descripcion
        self.codigos = codigos
        self.tipos = tipos

    def esAplicable(self, producto, cantidad):
        return producto.codigo in self.codigos or producto.tipo in self.tipos

    def aplicar(self, producto, cantidad):
        raise NotImplementedError("Método 'aplicar' debe ser implementado en las subclases")

class OfertaDescuento(Oferta):
    def __init__(self, descuento, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.descuento = descuento

    def aplicar(self, producto, cantidad):
        if self.esAplicable(producto, cantidad):
            return producto.precio * cantidad * (self.descuento / 100)
        return 0

class Oferta2x1(Oferta):
    def aplicar(self, producto, cantidad):
        if self.esAplicable(producto, cantidad):
            return producto.precio * (cantidad // 2)
        return 0

class Catalogo:
    def __init__(self):
        self.productos = []
        self.ofertas = []

    def leer(self, archivo):
        self.productos = []
        with open(archivo, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                codigo, nombre, precio, tipo, cantidad = row
                self.productos.append(Producto(codigo, nombre, float(precio), tipo, int(cantidad)))

    def guardar(self, archivo):
        with open(archivo, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['codigo', 'nombre', 'precio', 'tipo', 'cantidad'])
            for p in self.productos:
                writer.writerow([p.codigo, p.nombre, p.precio, p.tipo, p.cantidad])

    def agregar(self, producto):
        self.productos.append(producto)

    def buscar(self, codigo):
        for p in self.productos:
            if p.codigo == codigo:
                return p
        return None

    def registrarOferta(self, oferta):
        self.ofertas.append(oferta)

    def buscarOferta(self, producto, cantidad):
        for oferta in self.ofertas:
            if oferta.esAplicable(producto, cantidad):
                return oferta
        return None

    def calcularDescuento(self, producto, cantidad):
        oferta = self.buscarOferta(producto, cantidad)
        if oferta:
            return oferta.aplicar(producto, cantidad)
        return 0

    @property
    def cantidadProductos(self):
        return len(self.productos)

    @property
    def cantidadUnidades(self):
        return sum(p.cantidad for p in self.productos)

    @property
    def valorTotal(self):
        return sum(p.valorTotal() for p in self.productos)

    def informe(self):
        tipos = {}
        for p in self.productos:
            if p.tipo not in tipos:
                tipos[p.tipo] = {'unidades': 0, 'valor': 0}
            tipos[p.tipo]['unidades'] += p.cantidad
            tipos[p.tipo]['valor'] += p.valorTotal()

        informe = f"INFORME CATALOGO\n"
        informe += f"Cantidad de productos:   {self.cantidadProductos}\n"
        informe += f"Cantidad de unidades:    {self.cantidadUnidades}\n"
        informe += f"Precio promedio:       $ {self.valorTotal / self.cantidadUnidades:.2f}\n"
        informe += f"Valor total:           $ {self.valorTotal:.2f}\n"
        informe += "Tipos de productos:\n"
        for tipo, datos in tipos.items():
            precio_promedio = datos['valor'] / datos['unidades']
            informe += f"  - {tipo:<20}: {datos['unidades']:>4}u x $ {precio_promedio:.2f}\n"
        informe += "Ofertas:\n"
        for oferta in self.ofertas:
            informe += f"  - {oferta.descripcion}\n"
        return informe

class Cliente:
    def __init__(self, nombre, cuit):
        self.nombre = nombre
        self.cuit = cuit

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, value):
        if 1 <= len(value) <= 100:
            self._nombre = value
        else:
            raise ValueError("El nombre debe tener entre 1 y 100 caracteres")

    @property
    def cuit(self):
        return self._cuit

    @cuit.setter
    def cuit(self, value):
        if len(value) == 13 and value[2] == '-' and value[11] == '-' and value.replace('-', '').isdigit():
            self._cuit = value
        else:
            raise ValueError("El CUIT debe tener el formato XX-XXXXXXXX-X")

class Factura:
    _ultimo_numero = 0

    def __init__(self, catalogo, cliente):
        self.catalogo = catalogo
        self.cliente = cliente
        self.fecha = datetime.now()
        self.items = []
        Factura._ultimo_numero += 1
        self.numero = Factura._ultimo_numero

    @classmethod
    def ultimaFactura(cls, numero):
        cls._ultimo_numero = numero

    @classmethod
    def nuevoNumero(cls):
        cls._ultimo_numero += 1
        return cls._ultimo_numero

    def agregar(self, producto, cantidad):
        for item in self.items:
            if item['producto'] == producto:
                item['cantidad'] += cantidad
                return
        self.items.append({'producto': producto, 'cantidad': cantidad})

    @property
    def cantidadProductos(self):
        return len(self.items)

    @property
    def cantidadUnidades(self):
        return sum(item['cantidad'] for item in self.items)

    @property
    def subtotal(self):
        return sum(item['producto'].precio * item['cantidad'] for item in self.items)

    @property
    def descuentos(self):
        return sum(self.catalogo.calcularDescuento(item['producto'], item['cantidad']) for item in self.items)

    @property
    def total(self):
        return self.subtotal - self.descuentos

    def imprimir(self):
        factura = f"Factura: {self.numero}\n"
        factura += f"Fecha  : {self.fecha.strftime('%Y-%m-%d %H:%M:%S')}\n"
        factura += f"Cliente: {self.cliente.nombre} ({self.cliente.cuit})\n"
        for item in self.items:
            producto = item['producto']
            cantidad = item['cantidad']
            subtotal = producto.precio * cantidad
            factura += f"- {cantidad:2}u {producto.nombre:<30} x ${producto.precio:>7.2f} = ${subtotal:>9.2f}\n"
            descuento = self.catalogo.calcularDescuento(producto, cantidad)
            if descuento > 0:
                oferta = self.catalogo.buscarOferta(producto, cantidad)
                factura += f"      {oferta.descripcion:<40}     - ${descuento:>9.2f}\n"
        factura += f"{'Subtotal:':>54} ${self.subtotal:>9.2f}\n"
        factura += f"{'Descuentos:':>54} ${self.descuentos:>9.2f}\n"
        factura += f"{'-'*64}\n"
        factura += f"{'Total:':>54} ${self.total:>9.2f}"
        return factura
# Ejemplo de uso
if __name__ == "__main__":
    catalogo = Catalogo()
    catalogo.leer('catalogo.csv')

    # Registrar ofertas
    catalogo.registrarOferta(Oferta2x1("Oferta 2x1 en galletas", tipos=['galleta']))
    catalogo.registrarOferta(OfertaDescuento(20, "20% de descuento en gaseosas", tipos=['gaseosa']))

    # Crear cliente
    cliente = Cliente("Juan Perez", "20-12345678-9")

    # Crear factura
    factura = Factura(catalogo, cliente)

    # Agregar productos a la factura
    factura.agregar(catalogo.buscar('0001'), 2)  # 2 Coca Cola
    factura.agregar(catalogo.buscar('0003'), 3)  # 3 Sonrisa

    # Imprimir factura
    print(factura.imprimir())

    # Generar informe del catálogo
    print("\n" + catalogo.informe())