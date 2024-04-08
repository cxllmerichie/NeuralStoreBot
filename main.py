import handlers
import const


async def main():
    print('Loading...')  # TODO: logging
    await const.DATA.collect()
    print('Polling...')  # TODO: logging
    await handlers.DISPATCHER.start_polling()


if __name__ == '__main__':
    const.LOOP.run_until_complete(main())
