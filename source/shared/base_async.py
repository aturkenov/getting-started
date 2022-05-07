class BaseAsync:

    def __await__(
        self
    ):
        """
        """
        return self.__constructor().__await__()

    async def __constructor(
        self
    ):
        """
        """
        await self.__ainit__()
        return self

    async def __ainit__(
        self
    ):
        """
        """

