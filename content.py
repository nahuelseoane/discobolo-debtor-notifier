def content_email(first_name, amount):
    plain_content = f"""\
    Buenas tardes {first_name},

    De acuerdo con nuestros registros al día de la fecha, su cuenta presenta un saldo pendiente de ${amount:,.2f}.
    Le pedimos, por favor, que lo regularice a la brevedad.

    Aprovechamos para informarle que cerca del 60% de los compromisos del Club deben ser cubiertos antes del día 10 de cada mes, y más del 80% durante la primera quincena. 
    Por ello, su aporte puntual resulta fundamental para sostener la sana economía de nuestro querido Club.

    Agradecemos su colaboración y el compromiso individual de cada socio, que al multiplicarse fortalece a todo el Club y asegura su normal funcionamiento. 
    Es por ello que le invitamos a utilizar los medios de pago electrónicos y presenciales disponibles.

    En efectivo o cheque al día: acercándose al Club de martes a sábados de 8 a 20 hs y domingos de 8 a 12 hs.

    Mediante transferencia electrónica o e-cheq a la siguiente cuenta:
    CBU: 01400984 01503900332242
    CUIT: 30-52875094-6

    Para transferencias interbancarias:
    Cuenta corriente Nº: 3322/4
    Banco: Provincia de Buenos Aires
    Sucursal: Haedo (5039)

    Alias del banco: CLUB.DISCOBOLO

    En caso de haber abonado, desestime el mensaje.
    Ante cualquier duda, quedamos a disposición para brindar asistencia desde Secretaría.

    Con el afecto de siempre,

    Secretaría
    """

    html_content = f"""\
    <html>
    <body>
    <p>Buenas tardes <b>{first_name}</b>,</p>

    <p>De acuerdo con nuestros registros al día de la fecha, su cuenta presenta un saldo pendiente de <b>${amount:,.2f}</b>.<br>
    Le pedimos, por favor, que lo regularice a la brevedad.</p>

    <p>Aprovechamos para informarle que cerca del 60% de los compromisos del Club deben ser cubiertos antes del día 10 de cada mes, 
    y más del 80% durante la primera quincena. Por ello, su aporte puntual resulta fundamental para sostener la sana economía 
    de nuestro querido Club.</p>

    <p>Agradecemos su colaboración y el compromiso individual de cada socio, que al multiplicarse fortalece a todo el Club y asegura su normal funcionamiento. 
    Es por ello que le invitamos a utilizar los medios de pago electrónicos y presenciales disponibles.</p>

    <p><b>En efectivo o cheque al día:</b> acercándose al Club de martes a sábados de 8 a 20 hs y domingos de 8 a 12 hs.<br>
    <b>Transferencia electrónica o e-cheq:</b><br>
    CBU: 01400984 01503900332242<br>
    CUIT: 30-52875094-6<br>
    <b>Para transferencias interbancarias:</b><br>
    Cuenta corriente Nº: 3322/4<br>
    Banco: Provincia de Buenos Aires<br>
    Sucursal: Haedo (5039)</p>

    Alias del banco: <b>CLUB.DISCOBOLO</b>

    <p>En caso de haber abonado, desestime el mensaje.<br>
    Ante cualquier duda, quedamos a disposición para brindar asistencia desde Secretaría.</p>

    <p>Con el afecto de siempre,</p><br>
    
    <img src="cid:logo" alt="Club Logo" width="70">
    <strong>Secretaría</strong>
    <br>
    </body>
    </html>
    """
    return plain_content, html_content