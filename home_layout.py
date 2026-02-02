import dash
import dash_mantine_components as dmc


def layout_main():

    return dmc.MantineProvider([
        dmc.Flex([

            dmc.Title("Keycloak Application Dev"),
            dmc.Title(id='greetings-user'),
            dmc.Button(
                "Logout",
                id='logout-btn',
                variant="filled",
                color="#fa5c5c",
                size="sm",
                radius="sm",
                loading=False,
                disabled=False,
            )

        ], h="100dvh", justify="center", align="center", gap=20, direction="column")

    ])
