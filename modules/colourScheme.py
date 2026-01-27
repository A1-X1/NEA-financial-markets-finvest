from dataclasses import dataclass

@dataclass
class ColourScheme:
    def __init__(self, bg: str, surface: str, accent: str, btn_bg: str, btn_fg: str, 
                 text_p: str, text_s: str, text_ph: str, pos: str, neg: str,
                 sb_act_bg: str, sb_act_fg: str, sb_inact_bg: str, sb_inact_fg: str):
        self.__background = bg
        self.__surface = surface
        self.__accent = accent
        self.__button_background = btn_bg
        self.__button_foreground = btn_fg
        self.__text_primary = text_p
        self.__text_secondary = text_s
        self.__text_placeholder = text_ph
        self.__positive = pos
        self.__negative = neg
        self.__sb_active_bg = sb_act_bg
        self.__sb_active_fg = sb_act_fg
        self.__sb_inactive_bg = sb_inact_bg
        self.__sb_inactive_fg = sb_inact_fg

    @property
    def background(self) -> str:
        return self.__background

    @property
    def surface(self) -> str:
        return self.__surface

    @property
    def accent(self) -> str:
        return self.__accent

    @property
    def button_background(self) -> str:
        return self.__button_background

    @property
    def button_foreground(self) -> str:
        return self.__button_foreground

    @property
    def text_primary(self) -> str:
        return self.__text_primary

    @property
    def text_secondary(self) -> str:
        return self.__text_secondary

    @property
    def text_placeholder(self) -> str:
        return self.__text_placeholder

    @property
    def positive(self) -> str:
        return self.__positive

    @property
    def negative(self) -> str:
        return self.__negative

    @property
    def sb_active_bg(self) -> str:
        return self.__sb_active_bg

    @property
    def sb_active_fg(self) -> str:
        return self.__sb_active_fg

    @property
    def sb_inactive_bg(self) -> str:
        return self.__sb_inactive_bg

    @property
    def sb_inactive_fg(self) -> str:
        return self.__sb_inactive_fg
    
    @background.setter
    def background(self, value: str):
        self.__background = value

    @surface.setter
    def surface(self, value: str):
        self.__surface = value

    @accent.setter
    def accent(self, value: str):
        self.__accent = value

    @button_background.setter
    def button_background(self, value: str):
        self.__button_background = value

    @button_foreground.setter
    def button_foreground(self, value: str):
        self.__button_foreground = value

    @text_primary.setter
    def text_primary(self, value: str):
        self.__text_primary = value

    @text_secondary.setter
    def text_secondary(self, value: str):
        self.__text_secondary = value

    @text_placeholder.setter
    def text_placeholder(self, value: str):
        self.__text_placeholder = value

    @positive.setter
    def positive(self, value: str):
        self.__positive = value

    @negative.setter
    def negative(self, value: str):
        self.__negative = value

    @sb_active_bg.setter
    def sb_active_bg(self, value: str):
        self.__sb_active_bg = value

    @sb_active_fg.setter
    def sb_active_fg(self, value: str):
        self.__sb_active_fg = value

    @sb_inactive_bg.setter
    def sb_inactive_bg(self, value: str):
        self.__sb_inactive_bg = value

    @sb_inactive_fg.setter
    def sb_inactive_fg(self, value: str):
        self.__sb_inactive_fg = value
    

Theme = ColourScheme(
            bg='#FFFFFF',
            surface='#F8F8FA',
            accent='#24986D',
            btn_bg='#E2F0ED',
            btn_fg='#24986D',
            text_p='#0E7850',
            text_s='#000000',
            text_ph='#C4C4C4',
            pos='#10B981',
            neg='#EF4444',
            sb_act_bg='#E2F0ED',
            sb_act_fg='#24986D',
            sb_inact_bg='#F8F8FA',
            sb_inact_fg='#7C8D88'
        )

DarkTheme = ColourScheme(
            bg='#121212',           
            surface='#1E1E1E',      
            accent='#24986D',       
            btn_bg='#2D2D2D',       
            btn_fg='#24986D',       
            text_p='#FFFFFF',       
            text_s='#B0B0B0',      
            text_ph='#666666',      
            pos='#24986D',         
            neg='#CF6679',          
            sb_act_bg='#24986D1A', 
            sb_act_fg='#24986D',    
            sb_inact_bg='transparent', 
            sb_inact_fg='#757575'   
        )