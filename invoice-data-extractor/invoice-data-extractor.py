import sqlalchemy as db
import logging

logging.basicConfig(level="DEBUG")

log = logging.getLogger("INVOICE-EXTRACTOR")

def single_to_dict(result_set):
    return dict(zip(result_set[0].keys(), result_set[0]))

def multiple_to_dicts(result_set):
    return [dict(zip(row.keys(), row)) for row in result_set]


def get_pay_order_from_invoice(connection, pay_order_table, invoice_id):
    query = db.select([pay_order_table]).where(pay_order_table.c.invoice_id == invoice_id)
    result_proxy = connection.execute(query)
    result_set = result_proxy.fetchall()

    if not result_set:
        return None

    if len(result_set) != 1:
        raise Exception(f"Multiple pay orders for one invoice: {invoice_id}")

    return single_to_dict(result_set)



def get_invoice_by_id(connection, pay_invoice_table, invoice_id):
    query = db.select([pay_invoice_table]).where(pay_invoice_table.c.id == invoice_id)
    result_proxy = connection.execute(query)
    result_set = result_proxy.fetchall()
    if not result_set:
        return None
    if len(result_set) != 1:
        raise Exception(f"Multiple invoices with same id found: {invoice_id}")

    return single_to_dict(result_set)

def get_first_n_invoices(connection, pay_invoice_table, first_n_invoices):
    query = db.select([pay_invoice_table]).order_by(pay_invoice_table.c.timestamp.asc()).limit(first_n_invoices)
    result_proxy = connection.execute(query)
    result_set = result_proxy.fetchall()

    return multiple_to_dicts(result_set)


def get_last_n_invoices(connection, pay_invoice_table, last_n_invoices):
    query = db.select([pay_invoice_table]).order_by(pay_invoice_table.c.timestamp.desc()).limit(last_n_invoices)
    result_proxy = connection.execute(query)
    result_set = result_proxy.fetchall()

    return multiple_to_dicts(result_set)


def fetch_invoice_info():
    pass
    #pay_invoice_rows = cur.execute('''SELECT * FROM pay_invoice WHERE invoice_''').fetchall()

    #for row in pay_invoice_rows:
    #    print(row)


if __name__ == "__main__":
    print("Connecting to database payment.db...")
    engine_payment = db.create_engine('sqlite:///payment.db')
    engine_driver = db.create_engine('sqlite:///erc20-driver.db')
    connection_driver = engine_driver.connect()
    connection_payment = engine_payment.connect()

    metadata_payment = db.MetaData(engine_payment)
    metadata_driver = db.MetaData(engine_driver)

    pay_invoice_table = db.Table('pay_invoice', metadata_payment, autoload=True, autoload_with=engine_payment)
    pay_order_table = db.Table('pay_order', metadata_payment, autoload=True, autoload_with=engine_payment)


    print(pay_invoice_table.c)


    #print(get_invoice_by_id(pay_invoice_table, "4e537bb4-c3d0-4d58-a4d6-d265892087d5"))

    invoices = get_first_n_invoices(connection_payment, pay_invoice_table, 10)
    for invoice in invoices:
        log.debug(f"Checking invoice {invoice['id']}")
        pay_order = get_pay_order_from_invoice(connection_payment, pay_order_table, invoice["id"])
        if not pay_order:
            log.debug(f"Pay order for {invoice['id']} not found")

        else:
            log.debug(pay_order)
            if pay_order["driver"] == "erc20":
                log.debug(f"Checking payment for {invoice['id']} and order {pay_order['id']}")


