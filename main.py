import handlers
import loggers
import const


async def main():
    loggers.log.info('Loading...')
    await const.PRODUCTS.init()
    const.SCHEDULER.start()
    loggers.log.info('Polling...')
    await handlers.DISPATCHER.start_polling()


if __name__ == '__main__':
    const.LOOP.run_until_complete(main())
