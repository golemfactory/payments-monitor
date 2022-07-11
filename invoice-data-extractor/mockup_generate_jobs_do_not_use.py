import asyncio
import uuid

from datetime import datetime
import logging
import json

logging.basicConfig(level="DEBUG")
log = logging.getLogger("GOLEM-SIMULATOR")


def create_provider(id, node_name, payment_address, speed, overhead, cpu_cost, time_cost):
    provider = {
        "id": id,
        "node_name": node_name,
        "payment_address": payment_address,
        "speed": speed,
        "overhead": overhead,
        "cpu_cost": cpu_cost,
        "time_cost": time_cost,
    }
    return provider


provider_1 = create_provider("id_prov_1", "Provider1", "0x123", 30.56, 3.56, 13.0, 1.0)
provider_2 = create_provider("id_prov_2", "Provider2", "0x124", 16.56, 3.56, 9.0, 1.2)


job_template_1 = {
    "job_name": "test_fixing_primes",
    "job_quantity": 10.0,
    "job_unit": "primes",
    "job_length": 34.0,
}


async def do_job(job_template, provider):
    start_time = datetime.now()
    job_descriptor = {}
    job_descriptor["job_name"] = job_template["job_name"]
    job_descriptor["job_quantity"] = job_template["job_quantity"]
    job_descriptor["job_unit"] = job_template["job_unit"]

    job_descriptor["job_time"] = job_template["job_length"] / provider["speed"] + provider["overhead"]
    job_descriptor["cpu_time"] = job_template["job_length"] / provider["speed"]

    job_descriptor["job_cost"] = job_descriptor["job_time"] * provider["time_cost"] + job_descriptor["cpu_time"] * provider["cpu_cost"]


    log.debug(f"Job started on provider {provider['id']}")
    await asyncio.sleep(job_descriptor["job_time"])
    invoice_id = uuid.uuid4()

    log.debug(f"Job finished with cost {json.dumps(job_descriptor, indent=4)}")
    pass


async def main():
    print(uuid.uuid4())
    tasks = []
    tasks.append(asyncio.create_task(do_job(job_template_1, provider_1)))
    tasks.append(asyncio.create_task(do_job(job_template_1, provider_2)))


    for task in tasks:
        await task



asyncio.run(main())
