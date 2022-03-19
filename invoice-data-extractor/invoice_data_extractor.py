import sqlalchemy as db
import logging

logging.basicConfig(level="INFO")

log = logging.getLogger("INVOICE-EXTRACTOR")

def single_to_dict(result_set):
    return dict(zip(result_set[0].keys(), result_set[0]))

def multiple_to_dicts(result_set):
    return [dict(zip(row.keys(), row)) for row in result_set]

def get_transaction_by_tx_id(connection, erc20_transaction_table, tx_id):
    query = db.select([erc20_transaction_table]).where(erc20_transaction_table.c.tx_id == tx_id)
    result_proxy = connection.execute(query)
    result_set = result_proxy.fetchall()

    if not result_set:
        return None

    if len(result_set) != 1:
        raise Exception(f"Multiple transactions with the same id: {tx_id}")

    return single_to_dict(result_set)

def get_payment_from_order_id(connection, erc20_payment_table, order_id):
    query = db.select([erc20_payment_table]).where(erc20_payment_table.c.order_id == order_id)
    result_proxy = connection.execute(query)
    result_set = result_proxy.fetchall()

    if not result_set:
        return None

    if len(result_set) != 1:
        raise Exception(f"Multiple payments for one order: {order_id}")

    return single_to_dict(result_set)


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


def get_invoice_payment_status(connection_payment, connection_driver, pay_order_table, erc20_payment_table, erc20_transaction_table, invoice):
    result = dict()
    result["invoice_id"] = invoice["id"]
    result["transaction"] = None
    result["invoice_status"] = "UNKNOWN"

    log.debug(f"Checking invoice {invoice['id']}")
    pay_order = get_pay_order_from_invoice(connection_payment, pay_order_table, invoice["id"])
    if not pay_order:
        log.debug(f"Pay order for {invoice['id']} not found")
        return result

    log.debug(pay_order)
    result["invoice_status"] = "PAY_ORDER_FILLED"
    if pay_order["driver"] != "erc20":
        result["invoice_status"] = "UNSUPPORTED_DRIVER"
        return result

    order_id = pay_order['id']
    log.debug(f"Checking payment for {invoice['id']} and order {order_id}")
    erc20_payment = get_payment_from_order_id(connection_driver, erc20_payment_table, order_id)
    if not erc20_payment:
        log.debug(f"Not found payment related to order {order_id}")
        return result

    result["invoice_status"] = "PAYMENT_FOUND"
    log.debug(f"Payment found: {erc20_payment}")
    transaction_id = erc20_payment["tx_id"]
    if not transaction_id:
        return result

    erc20_transaction = get_transaction_by_tx_id(connection_driver, erc20_transaction_table, transaction_id)
    if not erc20_transaction:
        log.debug(f"erc20_transaction not found {transaction_id}")
        return result

    result["invoice_status"] = "TRANSACTION_FOUND"
    log.debug(f"Transaction found {erc20_transaction}")
    result["transaction"] = erc20_transaction

    return result


def main():
    print("Connecting to database payment.db...")
    engine_payment = db.create_engine('sqlite:///payment.db')
    engine_driver = db.create_engine('sqlite:///erc20-driver.db')
    connection_driver = engine_driver.connect()
    connection_payment = engine_payment.connect()

    metadata_payment = db.MetaData(engine_payment)
    metadata_driver = db.MetaData(engine_driver)

    pay_invoice_table = db.Table('pay_invoice', metadata_payment, autoload=True, autoload_with=engine_payment)
    pay_order_table = db.Table('pay_order', metadata_payment, autoload=True, autoload_with=engine_payment)

    erc20_payment_table = db.Table('payment', metadata_driver, autoload=True, autoload_with=engine_driver)
    erc20_transaction_table = db.Table('transaction', metadata_driver, autoload=True, autoload_with=engine_driver)



    print(pay_invoice_table.c)


    #print(get_invoice_by_id(pay_invoice_table, "4e537bb4-c3d0-4d58-a4d6-d265892087d5"))

    invoices = get_first_n_invoices(connection_payment, pay_invoice_table, 10000)
    for invoice in invoices:
        status = get_invoice_payment_status(connection_payment, connection_driver, pay_order_table, erc20_payment_table, erc20_transaction_table, invoice)
        print(status)








if __name__ == "__main__":
    main()




