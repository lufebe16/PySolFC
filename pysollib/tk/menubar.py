#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
##---------------------------------------------------------------------------##
##
## Copyright (C) 1998-2003 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2003 Mt. Hood Playing Card Co.
## Copyright (C) 2005-2009 Skomoroh
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
##---------------------------------------------------------------------------##

__all__ = ['PysolMenubarTk']

# imports
import math, os, sys, re
import Tkinter
import traceback
import tkFileDialog

# PySol imports
from pysollib.mygettext import _, n_
from pysollib.mfxutil import Struct, kwdefault
from pysollib.mfxutil import Image, USE_PIL
from pysollib.util import CARDSET
from pysollib.settings import TITLE, WIN_SYSTEM
from pysollib.settings import TOP_TITLE
from pysollib.settings import SELECT_GAME_MENU
from pysollib.settings import USE_FREECELL_SOLVER
from pysollib.settings import DEBUG
from pysollib.gamedb import GI

# toolkit imports
from pysollib.ui.tktile.tkconst import EVENT_HANDLED, EVENT_PROPAGATE, CURSOR_WATCH, COMPOUNDS
from pysollib.ui.tktile.tkutil import bind, after_idle
from tkwidget import MfxMessageDialog
from selectgame import SelectGameDialog, SelectGameDialogWithPreview
from soundoptionsdialog import SoundOptionsDialog
from selectcardset import SelectCardsetDialogWithPreview
from selecttile import SelectTileDialogWithPreview
from findcarddialog import connect_game_find_card_dialog, destroy_find_card_dialog
from solverdialog import connect_game_solver_dialog

from pysollib.ui.tktile.tkconst import TOOLBAR_BUTTONS

from pysollib.ui.tktile.menubar import createToolbarMenu, MfxMenubar, MfxMenu, PysolMenubarTkCommon
# ************************************************************************
# * - create menubar
# * - update menubar
# * - menu actions
# ************************************************************************

class PysolMenubarTk(PysolMenubarTkCommon):
    def __init__(self, app, top, progress=None):
        PysolMenubarTkCommon.__init__(self, app, top, progress)

    def _connect_game_find_card_dialog(self, game):
        return connect_game_find_card_dialog(game)

    def _destroy_find_card_dialog(self):
        return destroy_find_card_dialog()

    def _connect_game_solver_dialog(self, game):
        return connect_game_solver_dialog(game)

    #
    # create the menubar
    #

    def createThemesMenu(self, menu):
        return

    def _createMenubar(self):
        MfxMenubar.addPath = self._addPath
        kw = { "name": "menubar" }
        self.menubar = MfxMenubar(self.top, **kw)

        # init keybindings
        bind(self.top, "<KeyPress>", self._keyPressHandler)

        m = "Ctrl-"
        if sys.platform == "darwin": m = "Cmd-"

        if WIN_SYSTEM == "aqua":
            applemenu=MfxMenu(self.menubar, "apple")
            applemenu.add_command(label=_("&About ")+TITLE, command=self.mHelpAbout)

        menu = MfxMenu(self.menubar, n_("&File"))
        menu.add_command(label=n_("&New game"), command=self.mNewGame, accelerator="N")
        submenu = MfxMenu(menu, label=n_("R&ecent games"))
        ##menu.add_command(label=n_("Select &random game"), command=self.mSelectRandomGame, accelerator=m+"R")
        submenu = MfxMenu(menu, label=n_("Select &random game"))
        submenu.add_command(label=n_("&All games"), command=lambda : self.mSelectRandomGame('all'), accelerator=m+"R")
        submenu.add_command(label=n_("Games played and &won"), command=lambda : self.mSelectRandomGame('won'))
        submenu.add_command(label=n_("Games played and &not won"), command=lambda : self.mSelectRandomGame('not won'))
        submenu.add_command(label=n_("Games not &played"), command=lambda : self.mSelectRandomGame('not played'))
        menu.add_command(label=n_("Select game by nu&mber..."), command=self.mSelectGameById, accelerator=m+"M")
        menu.add_separator()
        submenu = MfxMenu(menu, label=n_("Fa&vorite games"))
        menu.add_command(label=n_("A&dd to favorites"), command=self.mAddFavor)
        menu.add_command(label=n_("Remove &from favorites"), command=self.mDelFavor)
        menu.add_separator()
        menu.add_command(label=n_("&Open..."), command=self.mOpen, accelerator=m+"O")
        menu.add_command(label=n_("&Save"), command=self.mSave, accelerator=m+"S")
        menu.add_command(label=n_("Save &as..."), command=self.mSaveAs)
        menu.add_command(label=n_("E&xport current layout..."), command=self.mExportCurrentLayout)
        menu.add_separator()
        menu.add_command(label=n_("&Hold and quit"), command=self.mHoldAndQuit, accelerator=m+"X")
        if WIN_SYSTEM != "aqua":
            menu.add_command(label=n_("&Quit"), command=self.mQuit, accelerator=m+"Q")

        if self.progress: self.progress.update(step=1)

        menu = MfxMenu(self.menubar, label=n_("&Select"))
        self._addSelectGameMenu(menu)

        if self.progress: self.progress.update(step=1)

        menu = MfxMenu(self.menubar, label=n_("&Edit"))
        menu.add_command(label=n_("&Undo"), command=self.mUndo, accelerator="Z")
        menu.add_command(label=n_("&Redo"), command=self.mRedo, accelerator="R")
        menu.add_command(label=n_("Redo &all"), command=self.mRedoAll)

        menu.add_separator()
        submenu = MfxMenu(menu, label=n_("&Set bookmark"))
        for i in range(9):
            label = _("Bookmark %d") % (i + 1)
            submenu.add_command(label=label, command=lambda i=i: self.mSetBookmark(i))
        submenu = MfxMenu(menu, label=n_("Go&to bookmark"))
        for i in range(9):
            label = _("Bookmark %d") % (i + 1)
            acc = m + "%d" % (i + 1)
            submenu.add_command(label=label, command=lambda i=i: self.mGotoBookmark(i), accelerator=acc)
        menu.add_command(label=n_("&Clear bookmarks"), command=self.mClearBookmarks)
        menu.add_separator()

        menu.add_command(label=n_("Restart"), command=self.mRestart, accelerator=m+"G")

        menu.add_separator()
        menu.add_command(label=n_("Solitaire &Wizard"), command=self.mWizard)
        menu.add_command(label=n_("&Edit current game"), command=self.mWizardEdit)

        menu = MfxMenu(self.menubar, label=n_("&Game"))
        menu.add_command(label=n_("&Deal cards"), command=self.mDeal, accelerator="D")
        menu.add_command(label=n_("&Auto drop"), command=self.mDrop, accelerator="A")
        menu.add_command(label=n_("Shu&ffle tiles"), command=self.mShuffle, accelerator="F")
        menu.add_checkbutton(label=n_("&Pause"), variable=self.tkopt.pause, command=self.mPause, accelerator="P")
        #menu.add_command(label=n_("&Pause"), command=self.mPause, accelerator="P")
        menu.add_separator()
        menu.add_command(label=n_("S&tatus..."), command=lambda : self.mPlayerStats(mode=100), accelerator=m+"Y")
        menu.add_checkbutton(label=n_("&Comments..."), variable=self.tkopt.comment, command=self.mEditGameComment)
        menu.add_separator()
        menu.add_command(label=n_("&Statistics..."), command=self.mPlayerStats, accelerator=m+"T")
        menu.add_command(label=n_("Log..."), command=lambda : self.mPlayerStats(mode=103))
        menu.add_separator()
        menu.add_command(label=n_("D&emo statistics"), command=lambda : self.mPlayerStats(mode=1101))

        menu = MfxMenu(self.menubar, label=n_("&Assist"))
        menu.add_command(label=n_("&Hint"), command=self.mHint, accelerator="H")
        menu.add_command(label=n_("Highlight p&iles"), command=self.mHighlightPiles, accelerator="I")
        menu.add_command(label=n_("&Find card"), command=self.mFindCard, accelerator="F3")
        menu.add_separator()
        menu.add_command(label=n_("&Demo"), command=self.mDemo, accelerator=m+"D")
        menu.add_command(label=n_("Demo (&all games)"), command=self.mMixedDemo)
        if USE_FREECELL_SOLVER:
            menu.add_command(label=n_("&Solver"), command=self.mSolver)
        else:
            menu.add_command(label=n_("&Solver"), state='disabled')
        menu.add_separator()
        menu.add_command(label=n_("&Piles description"), command=self.mStackDesk, accelerator="F2")

        if self.progress: self.progress.update(step=1)

        menu = MfxMenu(self.menubar, label=n_("&Options"))
        menu.add_command(label=n_("&Player options..."), command=self.mOptPlayerOptions)
        submenu = MfxMenu(menu, label=n_("&Automatic play"))
        submenu.add_checkbutton(label=n_("Auto &face up"), variable=self.tkopt.autofaceup, command=self.mOptAutoFaceUp)
        submenu.add_checkbutton(label=n_("A&uto drop"), variable=self.tkopt.autodrop, command=self.mOptAutoDrop)
        submenu.add_checkbutton(label=n_("Auto &deal"), variable=self.tkopt.autodeal, command=self.mOptAutoDeal)
        submenu.add_separator()
        submenu.add_checkbutton(label=n_("&Quick play"), variable=self.tkopt.quickplay, command=self.mOptQuickPlay)
        submenu = MfxMenu(menu, label=n_("Assist &level"))
        submenu.add_checkbutton(label=n_("Enable &undo"), variable=self.tkopt.undo, command=self.mOptEnableUndo)
        submenu.add_checkbutton(label=n_("Enable &bookmarks"), variable=self.tkopt.bookmarks, command=self.mOptEnableBookmarks)
        submenu.add_checkbutton(label=n_("Enable &hint"), variable=self.tkopt.hint, command=self.mOptEnableHint)
        submenu.add_checkbutton(label=n_("Enable shu&ffle"), variable=self.tkopt.shuffle, command=self.mOptEnableShuffle)
        submenu.add_checkbutton(label=n_("Enable highlight p&iles"), variable=self.tkopt.highlight_piles, command=self.mOptEnableHighlightPiles)
        submenu.add_checkbutton(label=n_("Enable highlight &cards"), variable=self.tkopt.highlight_cards, command=self.mOptEnableHighlightCards)
        submenu.add_checkbutton(label=n_("Enable highlight same &rank"), variable=self.tkopt.highlight_samerank, command=self.mOptEnableHighlightSameRank)
        submenu.add_checkbutton(label=n_("Highlight &no matching"), variable=self.tkopt.highlight_not_matching, command=self.mOptEnableHighlightNotMatching)
        submenu.add_separator()
        submenu.add_checkbutton(label=n_("&Show removed tiles (in Mahjongg games)"), variable=self.tkopt.mahjongg_show_removed, command=self.mOptMahjonggShowRemoved)
        submenu.add_checkbutton(label=n_("Show hint &arrow (in Shisen-Sho games)"), variable=self.tkopt.shisen_show_hint, command=self.mOptShisenShowHint)
        menu.add_separator()
        label = n_("&Sound...")
        if not self.app.audio.CAN_PLAY_SOUND:
            menu.add_checkbutton(label=label, variable=self.tkopt.sound, command=self.mOptSoundDialog, state='disabled')
        else:
            menu.add_checkbutton(label=label, variable=self.tkopt.sound, command=self.mOptSoundDialog)
        # cardsets
        if USE_PIL:
            submenu = MfxMenu(menu, label=n_("Card si&ze"))
            submenu.add_command(label=n_("&Increase the card size"), command=self.mIncreaseCardset, accelerator=m+"+")
            submenu.add_command(label=n_("&Decrease the card size"), command=self.mDecreaseCardset, accelerator=m+"-")
            submenu.add_checkbutton(label=n_("&Auto scaling"), variable=self.tkopt.auto_scale, command=self.mOptAutoScale, accelerator=m+'0')
        #manager = self.app.cardset_manager
        #n = manager.len()
        menu.add_command(label=n_("Cards&et..."), command=self.mSelectCardsetDialog, accelerator=m+"E")
        menu.add_command(label=n_("Table t&ile..."), command=self.mSelectTileDialog)
        # this submenu will get set by updateBackgroundImagesMenu()
        submenu = MfxMenu(menu, label=n_("Card &background"))
        submenu = MfxMenu(menu, label=n_("Card &view"))
        submenu.add_checkbutton(label=n_("Card shado&w"), variable=self.tkopt.shadow, command=self.mOptShadow)
        submenu.add_checkbutton(label=n_("Shade &legal moves"), variable=self.tkopt.shade, command=self.mOptShade)
        submenu.add_checkbutton(label=n_("&Negative cards bottom"), variable=self.tkopt.negative_bottom, command=self.mOptNegativeBottom)
        submenu.add_checkbutton(label=n_("Shrink face-down cards"), variable=self.tkopt.shrink_face_down, command=self.mOptShrinkFaceDown)
        submenu.add_checkbutton(label=n_("Shade &filled stacks"), variable=self.tkopt.shade_filled_stacks, command=self.mOptShadeFilledStacks)
        submenu = MfxMenu(menu, label=n_("A&nimations"))
        submenu.add_radiobutton(label=n_("&None"), variable=self.tkopt.animations, value=0, command=self.mOptAnimations)
        submenu.add_radiobutton(label=n_("&Very fast"), variable=self.tkopt.animations, value=1, command=self.mOptAnimations)
        submenu.add_radiobutton(label=n_("&Fast"), variable=self.tkopt.animations, value=2, command=self.mOptAnimations)
        submenu.add_radiobutton(label=n_("&Medium"), variable=self.tkopt.animations, value=3, command=self.mOptAnimations)
        submenu.add_radiobutton(label=n_("&Slow"), variable=self.tkopt.animations, value=4, command=self.mOptAnimations)
        submenu.add_radiobutton(label=n_("V&ery slow"), variable=self.tkopt.animations, value=5, command=self.mOptAnimations)
        submenu.add_separator()
        submenu.add_checkbutton(label=n_("&Redeal animation"), variable=self.tkopt.redeal_animation, command=self.mRedealAnimation)
        if Image:
            submenu.add_checkbutton(label=n_("&Winning animation"), variable=self.tkopt.win_animation, command=self.mWinAnimation)
        submenu = MfxMenu(menu, label=n_("&Mouse"))
        submenu.add_radiobutton(label=n_("&Drag-and-Drop"), variable=self.tkopt.mouse_type, value='drag-n-drop', command=self.mOptMouseType)
        submenu.add_radiobutton(label=n_("&Point-and-Click"), variable=self.tkopt.mouse_type, value='point-n-click', command=self.mOptMouseType)
        submenu.add_radiobutton(label=n_("&Sticky mouse"), variable=self.tkopt.mouse_type, value='sticky-mouse', command=self.mOptMouseType)
        submenu.add_separator()
        submenu.add_checkbutton(label=n_("Use mouse for undo/redo"), variable=self.tkopt.mouse_undo, command=self.mOptMouseUndo)
        menu.add_separator()
        menu.add_command(label=n_("&Fonts..."), command=self.mOptFonts)
        menu.add_command(label=n_("&Colors..."), command=self.mOptColors)
        menu.add_command(label=n_("Time&outs..."), command=self.mOptTimeouts)
        menu.add_separator()
        self.createThemesMenu(menu)
        submenu = MfxMenu(menu, label=n_("&Toolbar"))
        createToolbarMenu(self, submenu)
        submenu = MfxMenu(menu, label=n_("Stat&usbar"))
        submenu.add_checkbutton(label=n_("Show &statusbar"), variable=self.tkopt.statusbar, command=self.mOptStatusbar)
        submenu.add_checkbutton(label=n_("Show &number of cards"), variable=self.tkopt.num_cards, command=self.mOptNumCards)
        submenu.add_checkbutton(label=n_("Show &help bar"), variable=self.tkopt.helpbar, command=self.mOptHelpbar)
        if not USE_PIL:
            menu.add_checkbutton(label=n_("Save games &geometry"), variable=self.tkopt.save_games_geometry, command=self.mOptSaveGamesGeometry)
        menu.add_checkbutton(label=n_("&Demo logo"), variable=self.tkopt.demo_logo, command=self.mOptDemoLogo)
        menu.add_checkbutton(label=n_("Startup splash sc&reen"), variable=self.tkopt.splashscreen, command=self.mOptSplashscreen)
###        menu.add_separator()
###        menu.add_command(label="Save options", command=self.mOptSave)

        if self.progress: self.progress.update(step=1)

        menu = MfxMenu(self.menubar, label=n_("&Help"))
        menu.add_command(label=n_("&Contents"), command=self.mHelp, accelerator=m+"F1")
        menu.add_command(label=n_("&How to play"), command=self.mHelpHowToPlay)
        menu.add_command(label=n_("&Rules for this game"), command=self.mHelpRules, accelerator="F1")
        menu.add_command(label=n_("&License terms"), command=self.mHelpLicense)
        ##menu.add_command(label=n_("What's &new ?"), command=self.mHelpNews)
        if WIN_SYSTEM != "aqua":
            menu.add_separator()
            menu.add_command(label=n_("&About ")+TITLE+"...", command=self.mHelpAbout)

        MfxMenubar.addPath = None

        ### FIXME: all key bindings should be *added* to keyPressHandler
        ctrl = "Control-"
        if sys.platform == "darwin": ctrl = "Command-"
        self._bindKey("",   "n", self.mNewGame)
        self._bindKey(ctrl, "w", self.mSelectGameDialog)
        self._bindKey(ctrl, "v", self.mSelectGameDialogWithPreview)
        self._bindKey(ctrl, "r", lambda e: self.mSelectRandomGame())
        self._bindKey(ctrl, "m", self.mSelectGameById)
        self._bindKey(ctrl, "n", self.mNewGameWithNextId)
        self._bindKey(ctrl, "o", self.mOpen)
        self._bindKey(ctrl, "s", self.mSave)
        self._bindKey(ctrl, "x", self.mHoldAndQuit)
        self._bindKey(ctrl, "q", self.mQuit)
        self._bindKey("",   "z", self.mUndo)
        self._bindKey("",   "BackSpace", self.mUndo)    # undocumented
        self._bindKey("",   "KP_Enter", self.mUndo)     # undocumented
        self._bindKey("",   "r", self.mRedo)
        self._bindKey(ctrl, "g", self.mRestart)
        self._bindKey("",   "space", self.mDeal)        # undocumented
        self._bindKey(ctrl, "y", lambda e: self.mPlayerStats(mode=100))
        self._bindKey(ctrl, "t", lambda e: self.mPlayerStats(mode=105))
        self._bindKey("",   "h", self.mHint)
        self._bindKey(ctrl, "h", self.mHint1)           # undocumented
        ##self._bindKey("",   "Shift_L", self.mHighlightPiles)
        ##self._bindKey("",   "Shift_R", self.mHighlightPiles)
        self._bindKey("",   "i", self.mHighlightPiles)
        self._bindKey("",   "F3", self.mFindCard)
        self._bindKey(ctrl, "d", self.mDemo)
        self._bindKey(ctrl, "e", self.mSelectCardsetDialog)
        if USE_PIL:
            self._bindKey(ctrl, "plus", self.mIncreaseCardset)
            self._bindKey(ctrl, "equal", self.mIncreaseCardset)
            self._bindKey(ctrl, "minus", self.mDecreaseCardset)
            self._bindKey(ctrl, "0", self.mOptAutoScale)
        self._bindKey(ctrl, "b", self.mOptChangeCardback) # undocumented
        self._bindKey(ctrl, "i", self.mOptChangeTableTile) # undocumented
        self._bindKey(ctrl, "p", self.mOptPlayerOptions)   # undocumented
        self._bindKey(ctrl, "F1", self.mHelp)
        self._bindKey("",   "F1", self.mHelpRules)
        self._bindKey("",   "Print", self.mScreenshot)
        self._bindKey(ctrl, "u", self.mPlayNextMusic)   # undocumented
        self._bindKey("",   "p", self.mPause)
        self._bindKey("",   "Pause", self.mPause)       # undocumented
        self._bindKey("",   "Escape", self.mIconify)    # undocumented
        # ASD and LKJ
        self._bindKey("",   "a", self.mDrop)
        self._bindKey(ctrl, "a", self.mDrop1)
        self._bindKey("",   "s", self.mUndo)
        self._bindKey("",   "d", self.mDeal)
        self._bindKey("",   "l", self.mDrop)
        self._bindKey(ctrl, "l", self.mDrop1)
        self._bindKey("",   "k", self.mUndo)
        self._bindKey("",   "j", self.mDeal)

        self._bindKey("",   "F2", self.mStackDesk)
        #
        self._bindKey("", "slash", lambda e: self.mPlayerStats(mode=106)) # undocumented, devel
        #
        self._bindKey("",   "f", self.mShuffle)

        for i in range(9):
            self._bindKey(ctrl, str(i+1),  lambda e, i=i: self.mGotoBookmark(i, confirm=0))

        # undocumented, devel
        self._bindKey(ctrl, "End", self.mPlayNextMusic)
        self._bindKey(ctrl, "Prior", self.mSelectPrevGameByName)
        self._bindKey(ctrl, "Next", self.mSelectNextGameByName)
        self._bindKey(ctrl, "Up", self.mSelectPrevGameById)
        self._bindKey(ctrl, "Down", self.mSelectNextGameById)


    #
    # key binding utility
    #

    def _bindKey(self, modifier, key, func):
##         if 0 and not modifier and len(key) == 1:
##             self.keybindings[key.lower()] = func
##             self.keybindings[key.upper()] = func
##             return
        if not modifier and len(key) == 1:
            # ignore Ctrl/Shift/Alt
            # but don't ignore NumLock (state == 16)
            func = lambda e, func=func: e.state in (0, 16) and func(e)
        sequence = "<" + modifier + "KeyPress-" + key + ">"
        bind(self.top, sequence, func)
        if len(key) == 1 and key != key.upper():
            key = key.upper()
            sequence = "<" + modifier + "KeyPress-" + key + ">"
            bind(self.top, sequence, func)


    def _keyPressHandler(self, event):
        r = EVENT_PROPAGATE
        if event and self.game:
            ##print event.__dict__
            if self.game.demo:
                # stop the demo by setting self.game.demo.keypress
                if event.char:    # ignore Ctrl/Shift/etc.
                    self.game.demo.keypress = event.char
                    r = EVENT_HANDLED
##             func = self.keybindings.get(event.char)
##             if func and (event.state & ~2) == 0:
##                 func(event)
##                 r = EVENT_HANDLED
        return r

    #
    # Select Game menu creation
    #

    def _addSelectGameMenu(self, menu):
        #games = map(self.app.gdb.get, self.app.gdb.getGamesIdSortedByShortName())
        games = map(self.app.gdb.get, self.app.gdb.getGamesIdSortedByName())
        ##games = tuple(games)
        ###menu = MfxMenu(menu, label="Select &game")
        m = "Ctrl-"
        if sys.platform == "darwin": m = "Cmd-"
        menu.add_command(label=n_("All &games..."), accelerator=m+"W",
                         command=self.mSelectGameDialog)
        menu.add_command(label=n_("Playable pre&view..."), accelerator=m+"V",
                         command=self.mSelectGameDialogWithPreview)
        if not SELECT_GAME_MENU:
            return
        menu.add_separator()
        self._addSelectPopularGameSubMenu(games, menu, self.mSelectGame,
                                          self.tkopt.gameid)
        self._addSelectFrenchGameSubMenu(games, menu, self.mSelectGame,
                                         self.tkopt.gameid)
        if self.progress: self.progress.update(step=1)
        self._addSelectMahjonggGameSubMenu(games, menu, self.mSelectGame,
                                           self.tkopt.gameid)
        self._addSelectOrientalGameSubMenu(games, menu, self.mSelectGame,
                                           self.tkopt.gameid)
        self._addSelectSpecialGameSubMenu(games, menu, self.mSelectGame,
                                          self.tkopt.gameid)
        self._addSelectCustomGameSubMenu(games, menu, self.mSelectGame,
                                         self.tkopt.gameid)
        menu.add_separator()
        if self.progress: self.progress.update(step=1)
        self._addSelectAllGameSubMenu(games, menu, self.mSelectGame,
                                      self.tkopt.gameid)


    def _addSelectGameSubMenu(self, games, menu, select_data,
                              command, variable):
        ##print select_data
        need_sep = 0
        for label, select_func in select_data:
            if label is None:
                need_sep = 1
                continue
            g = filter(select_func, games)
            if not g:
                continue
            if need_sep:
                menu.add_separator()
                need_sep = 0
            submenu = MfxMenu(menu, label=label)
            self._addSelectGameSubSubMenu(g, submenu, command, variable)

    def _getNumGames(self, games, select_data):
        ngames = 0
        for label, select_func in select_data:
            ngames += len(filter(select_func, games))
        return ngames

    def _addSelectMahjonggGameSubMenu(self, games, menu, command, variable):
        select_func = lambda gi: gi.si.game_type == GI.GT_MAHJONGG
        mahjongg_games = filter(select_func, games)
        if len(mahjongg_games) == 0:
            return
        #
        menu = MfxMenu(menu, label=n_("&Mahjongg games"))

        def add_menu(games, c0, c1, menu=menu,
                     variable=variable, command=command):
            if not games:
                return
            label = c0 + ' - ' + c1
            if c0 == c1:
                label = c0
            submenu = MfxMenu(menu, label=label, name=None)
            self._addSelectGameSubSubMenu(games, submenu, command,
                                          variable, short_name=True)

        games = {}
        for gi in mahjongg_games:
            c = gi.short_name.strip()[0]
            if c in games:
                games[c].append(gi)
            else:
                games[c] = [gi]
        games = games.items()
        games.sort()
        g0 = []
        c0 = c1 = games[0][0]
        for c, g1 in games:
            if len(g0)+len(g1) >= self.cb_max:
                add_menu(g0, c0, c1)
                g0 = g1
                c0 = c1 = c
            else:
                g0 += g1
                c1 = c
        add_menu(g0, c0, c1)

    def _addSelectPopularGameSubMenu(self, games, menu, command, variable):
        select_func = lambda gi: gi.si.game_flags & GI.GT_POPULAR
        if len(filter(select_func, games)) == 0:
            return
        data = (n_("&Popular games"), select_func)
        self._addSelectGameSubMenu(games, menu, (data, ),
                                   self.mSelectGamePopular,
                                   self.tkopt.gameid_popular)

    def _addSelectFrenchGameSubMenu(self, games, menu, command, variable):
        if self._getNumGames(games, GI.SELECT_GAME_BY_TYPE) == 0:
            return
        submenu = MfxMenu(menu, label=n_("&French games"))
        self._addSelectGameSubMenu(games, submenu, GI.SELECT_GAME_BY_TYPE,
                                   self.mSelectGame, self.tkopt.gameid)

    def _addSelectOrientalGameSubMenu(self, games, menu, command, variable):
        if self._getNumGames(games, GI.SELECT_ORIENTAL_GAME_BY_TYPE) == 0:
            return
        submenu = MfxMenu(menu, label=n_("&Oriental games"))
        self._addSelectGameSubMenu(games, submenu,
                                   GI.SELECT_ORIENTAL_GAME_BY_TYPE,
                                   self.mSelectGame, self.tkopt.gameid)

    def _addSelectSpecialGameSubMenu(self, games, menu, command, variable):
        if self._getNumGames(games, GI.SELECT_ORIENTAL_GAME_BY_TYPE) == 0:
            return
        submenu = MfxMenu(menu, label=n_("&Special games"))
        self._addSelectGameSubMenu(games, submenu,
                                   GI.SELECT_SPECIAL_GAME_BY_TYPE,
                                   self.mSelectGame, self.tkopt.gameid)

    def _addSelectCustomGameSubMenu(self, games, menu, command, variable):
        submenu = MfxMenu(menu, label=n_("&Custom games"))
        select_func = lambda gi: gi.si.game_type == GI.GT_CUSTOM
        games = filter(select_func, games)
        self.updateGamesMenu(submenu, games)

    def _addSelectAllGameSubMenu(self, games, menu, command, variable):
        menu = MfxMenu(menu, label=n_("&All games by name"))
        n, d = 0, self.cb_max
        i = 0
        while True:
            if self.progress: self.progress.update(step=1)
            columnbreak = i > 0 and (i % d) == 0
            i += 1
            if not games[n:n+d]:
                break
            m = min(n+d-1, len(games)-1)
            label = games[n].name[:3] + ' - ' + games[m].name[:3]
            submenu = MfxMenu(menu, label=label, name=None)
            self._addSelectGameSubSubMenu(games[n:n+d], submenu,
                                          command, variable)
            n += d
            if columnbreak:
                menu.entryconfigure(i, columnbreak=columnbreak)

    def _addSelectGameSubSubMenu(self, games, menu, command, variable,
                                 short_name=False):
        ##cb = (25, self.cb_max) [ len(g) > 4 * 25 ]
        ##cb = min(cb, self.cb_max)
        cb = self.cb_max
        for i in range(len(games)):
            gi = games[i]
            columnbreak = i > 0 and (i % cb) == 0
            if short_name:
                label = gi.short_name
            else:
                label = gi.name
            # optimized by inlining
            menu.tk.call((menu._w, 'add', 'radiobutton') +
                         menu._options({'command': command,
                                        'variable': variable,
                                        'columnbreak': columnbreak,
                                        'value': gi.id,
                                        'label': label}))

    def updateGamesMenu(self, menu, games):
        menu.delete(0, 'last')
        if len(games) == 0:
            menu.add_radiobutton(label='<none>', name=None, state='disabled')
        elif len(games) > self.cb_max*4:
            games.sort(lambda a, b: cmp(a.name, b.name))
            self._addSelectAllGameSubMenu(games, menu,
                                          command=self.mSelectGame,
                                          variable=self.tkopt.gameid)
        else:
            self._addSelectGameSubSubMenu(games, menu,
                                          command=self.mSelectGame,
                                          variable=self.tkopt.gameid)

    #
    # Select Game menu actions
    #

    def mSelectGame(self, *args):
        self._mSelectGame(self.tkopt.gameid.get())

    def mSelectGamePopular(self, *args):
        self._mSelectGame(self.tkopt.gameid_popular.get())

    def _mSelectGameDialog(self, d):
        if d.status == 0 and d.button == 0 and d.gameid != self.game.id:
            self.tkopt.gameid.set(d.gameid)
            self.tkopt.gameid_popular.set(d.gameid)
            if 0:
                self._mSelectGame(d.gameid, random=d.random)
            else:
                # don't ask areYouSure()
                self._cancelDrag()
                self.game.endGame()
                self.game.quitGame(d.gameid, random=d.random)
        return EVENT_HANDLED

    def __restoreCursor(self, *event):
        self.game.setCursor(cursor=self.app.top_cursor)

    def mSelectGameDialog(self, *event):
        if self._cancelDrag(break_pause=False): return
        self.game.setCursor(cursor=CURSOR_WATCH)
        after_idle(self.top, self.__restoreCursor)
        d = SelectGameDialog(self.top, title=_("Select game"),
                             app=self.app, gameid=self.game.id)
        return self._mSelectGameDialog(d)

    def mSelectGameDialogWithPreview(self, *event):
        if self._cancelDrag(break_pause=False): return
        self.game.setCursor(cursor=CURSOR_WATCH)
        bookmark = None
        if 0:
            # use a bookmark for our preview game
            if self.game.setBookmark(-2, confirm=0):
                bookmark = self.game.gsaveinfo.bookmarks[-2][0]
                del self.game.gsaveinfo.bookmarks[-2]
        after_idle(self.top, self.__restoreCursor)
        d = SelectGameDialogWithPreview(self.top, title=_("Select game"),
                                        app=self.app, gameid=self.game.id,
                                        bookmark=bookmark)
        return self._mSelectGameDialog(d)


    #
    # menubar overrides
    #

    def updateFavoriteGamesMenu(self):
        gameids = self.app.opt.favorite_gameid
        submenu = self.menupath[".menubar.file.favoritegames"][2]
        games = []
        for id in gameids:
            gi = self.app.getGameInfo(id)
            if gi:
                games.append(gi)
        self.updateGamesMenu(submenu, games)
        state = self._getEnabledState
        in_favor = self.app.game.id in gameids
        menu, index, submenu = self.menupath[".menubar.file.addtofavorites"]
        menu.entryconfig(index, state=state(not in_favor))
        menu, index, submenu = self.menupath[".menubar.file.removefromfavorites"]
        menu.entryconfig(index, state=state(in_favor))


    def updateRecentGamesMenu(self, gameids):
        submenu = self.menupath[".menubar.file.recentgames"][2]
        games = []
        for id in gameids:
            gi = self.app.getGameInfo(id)
            if gi:
                games.append(gi)
        self.updateGamesMenu(submenu, games)

    def updateBookmarkMenuState(self):
        state = self._getEnabledState
        mp1 = self.menupath.get(".menubar.edit.setbookmark")
        mp2 = self.menupath.get(".menubar.edit.gotobookmark")
        mp3 = self.menupath.get(".menubar.edit.clearbookmarks")
        if mp1 is None or mp2 is None or mp3 is None:
            return
        x = self.app.opt.bookmarks and self.game.canSetBookmark()
        #
        menu, index, submenu = mp1
        for i in range(9):
            submenu.entryconfig(i, state=state(x))
        menu.entryconfig(index, state=state(x))
        #
        menu, index, submenu = mp2
        ms = 0
        for i in range(9):
            s = self.game.gsaveinfo.bookmarks.get(i) is not None
            submenu.entryconfig(i, state=state(s and x))
            ms = ms or s
        menu.entryconfig(index, state=state(ms and x))
        #
        menu, index, submenu = mp3
        menu.entryconfig(index, state=state(ms and x))

    def updateBackgroundImagesMenu(self):
        mp = self.menupath.get(".menubar.options.cardbackground")
        # delete all entries
        submenu = mp[2]
        submenu.delete(0, "last")
        # insert new cardbacks
        mbacks = self.app.images.getCardbacks()
        cb = int(math.ceil(math.sqrt(len(mbacks))))
        for i in range(len(mbacks)):
            columnbreak = i > 0 and (i % cb) == 0
            submenu.add_radiobutton(label=mbacks[i].name, image=mbacks[i].menu_image, variable=self.tkopt.cardback, value=i,
                                    command=self.mOptCardback, columnbreak=columnbreak, indicatoron=0, hidemargin=0)


    #
    # menu updates
    #

    def setMenuState(self, state, path):
        #print state, path
        path = ".menubar." + path
        mp = self.menupath.get(path)
        menu, index, submenu = mp
        s = self._getEnabledState(state)
        menu.entryconfig(index, state=s)

    def setToolbarState(self, state, path):
        #print state, path
        s = self._getEnabledState(state)
        w = getattr(self.app.toolbar, path + "_button")
        w["state"] = s

    def _setCommentMenu(self, v):
        self.tkopt.comment.set(v)

    def _setPauseMenu(self, v):
        self.tkopt.pause.set(v)


    #
    # menu actions
    #

    DEFAULTEXTENSION = ".pso"
    FILETYPES = ((TITLE+" files", "*"+DEFAULTEXTENSION), ("All files", "*"))

    def mAddFavor(self, *event):
        gameid = self.app.game.id
        if gameid not in self.app.opt.favorite_gameid:
            self.app.opt.favorite_gameid.append(gameid)
            self.updateFavoriteGamesMenu()

    def mDelFavor(self, *event):
        gameid = self.app.game.id
        if gameid in self.app.opt.favorite_gameid:
            self.app.opt.favorite_gameid.remove(gameid)
            self.updateFavoriteGamesMenu()

    def mOpen(self, *event):
        if self._cancelDrag(break_pause=False): return
        filename = self.game.filename
        if filename:
            idir, ifile = os.path.split(os.path.normpath(filename))
        else:
            idir, ifile = "", ""
        if not idir:
            idir = self.app.dn.savegames
        d = tkFileDialog.Open()
        filename = d.show(filetypes=self.FILETYPES,
                          defaultextension=self.DEFAULTEXTENSION,
                          initialdir=idir, initialfile=ifile)
        if filename:
            filename = os.path.normpath(filename)
            ##filename = os.path.normcase(filename)
            if os.path.isfile(filename):
                self.game.loadGame(filename)

    def mExportCurrentLayout(self, *event):
        if self._cancelDrag(break_pause=False): return
        game = self.game
        if not self.menustate.save_as:
            return
        if not game.Solver_Class:
            d = MfxMessageDialog(self.top, title=_('Export game error'),
                                     text=_('''
Unsupported game for export.
'''),
                                     bitmap='error')
            return

        filename = game.filename
        if not filename:
            filename = self.app.getGameSaveName(self.game.id)
            if os.name == "posix" or os.path.supports_unicode_filenames:
                filename += "-" + self.game.getGameNumber(format=0)
            else:
                filename += "-01"
            filename += ".board"
        idir, ifile = os.path.split(os.path.normpath(filename))
        if not idir:
            idir = self.app.dn.savegames
        ##print self.game.filename, ifile
        d = tkFileDialog.SaveAs()
        filename = d.show(filetypes=self.FILETYPES,
                          defaultextension=self.DEFAULTEXTENSION,
                          initialdir=idir, initialfile=ifile)
        if filename:
            filename = os.path.normpath(filename)
            ##filename = os.path.normcase(filename)
            with open(filename, 'w') as fh:
                game = self.game
                fh.write(game.Solver_Class(game, self).calcBoardString())
            self.updateMenus()

    def mSaveAs(self, *event):
        if self._cancelDrag(break_pause=False): return
        if not self.menustate.save_as:
            return
        filename = self.game.filename
        if not filename:
            filename = self.app.getGameSaveName(self.game.id)
            if os.name == "posix":
                filename = filename + "-" + self.game.getGameNumber(format=0)
            elif os.path.supports_unicode_filenames: # new in python 2.3
                filename = filename + "-" + self.game.getGameNumber(format=0)
            else:
                filename = filename + "-01"
            filename = filename + self.DEFAULTEXTENSION
        idir, ifile = os.path.split(os.path.normpath(filename))
        if not idir:
            idir = self.app.dn.savegames
        ##print self.game.filename, ifile
        d = tkFileDialog.SaveAs()
        filename = d.show(filetypes=self.FILETYPES,
                          defaultextension=self.DEFAULTEXTENSION,
                          initialdir=idir, initialfile=ifile)
        if filename:
            filename = os.path.normpath(filename)
            ##filename = os.path.normcase(filename)
            self.game.saveGame(filename)
            self.updateMenus()

    def mPause(self, *args):
        if not self.game:
            return
        if not self.game.pause:
            if self._cancelDrag(): return
        self.game.doPause()
        self.tkopt.pause.set(self.game.pause)

    def mOptSoundDialog(self, *args):
        if self._cancelDrag(break_pause=False): return
        d = SoundOptionsDialog(self.top, _("Sound settings"), self.app)
        self.tkopt.sound.set(self.app.opt.sound)

    def mOptAutoFaceUp(self, *args):
        if self._cancelDrag(): return
        self.app.opt.autofaceup = self.tkopt.autofaceup.get()
        if self.app.opt.autofaceup:
            self.game.autoPlay()

    def mOptAutoDrop(self, *args):
        if self._cancelDrag(): return
        self.app.opt.autodrop = self.tkopt.autodrop.get()
        if self.app.opt.autodrop:
            self.game.autoPlay()

    def mOptAutoDeal(self, *args):
        if self._cancelDrag(): return
        self.app.opt.autodeal = self.tkopt.autodeal.get()
        if self.app.opt.autodeal:
            self.game.autoPlay()

    def mOptQuickPlay(self, *args):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.quickplay = self.tkopt.quickplay.get()

    def mOptEnableUndo(self, *args):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.undo = self.tkopt.undo.get()
        self.game.updateMenus()

    def mOptEnableBookmarks(self, *args):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.bookmarks = self.tkopt.bookmarks.get()
        self.game.updateMenus()

    def mOptEnableHint(self, *args):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.hint = self.tkopt.hint.get()
        self.game.updateMenus()

    def mOptEnableShuffle(self, *args):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.shuffle = self.tkopt.shuffle.get()
        self.game.updateMenus()

    def mOptEnableHighlightPiles(self, *args):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.highlight_piles = self.tkopt.highlight_piles.get()
        self.game.updateMenus()

    def mOptEnableHighlightCards(self, *args):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.highlight_cards = self.tkopt.highlight_cards.get()
        self.game.updateMenus()

    def mOptEnableHighlightSameRank(self, *args):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.highlight_samerank = self.tkopt.highlight_samerank.get()
        ##self.game.updateMenus()

    def mOptEnableHighlightNotMatching(self, *args):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.highlight_not_matching = self.tkopt.highlight_not_matching.get()
        ##self.game.updateMenus()

    def mOptAnimations(self, *args):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.animations = self.tkopt.animations.get()

    def mRedealAnimation(self, *args):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.redeal_animation = self.tkopt.redeal_animation.get()

    def mWinAnimation(self, *args):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.win_animation = self.tkopt.win_animation.get()

    def mOptShadow(self, *args):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.shadow = self.tkopt.shadow.get()

    def mOptShade(self, *args):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.shade = self.tkopt.shade.get()

    def mOptShrinkFaceDown(self, *args):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.shrink_face_down = self.tkopt.shrink_face_down.get()
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)

    def mOptShadeFilledStacks(self, *args):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.shade_filled_stacks = self.tkopt.shade_filled_stacks.get()
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)

    def mOptMahjonggShowRemoved(self, *args):
        if self._cancelDrag(): return
        self.app.opt.mahjongg_show_removed = self.tkopt.mahjongg_show_removed.get()
        ##self.game.updateMenus()
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)

    def mOptShisenShowHint(self, *args):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.shisen_show_hint = self.tkopt.shisen_show_hint.get()
        ##self.game.updateMenus()

    def _updateCardSize(self):
        geom = (self.app.canvas.winfo_width(),
                self.app.canvas.winfo_height())
        self.app.opt.game_geometry = geom
        self.app.game.resizeGame()
        if self.app.opt.auto_scale:
            w, h = self.app.opt.game_geometry
            self.app.canvas.setInitialSize(w, h, scrollregion=False)
        else:
            w = int(round(self.app.game.width * self.app.opt.scale_x))
            h = int(round(self.app.game.height * self.app.opt.scale_y))
            self.app.canvas.setInitialSize(w, h)
            self.app.top.wm_geometry("")    # cancel user-specified geometry
        ##self.app.top.update_idletasks()

    def mIncreaseCardset(self, *event):
        if self._cancelDrag(break_pause=True): return
        if self.app.opt.scale_x < 4:
            self.app.opt.scale_x += 0.1
        else:
            return
        if self.app.opt.scale_y < 4:
            self.app.opt.scale_y += 0.1
        else:
            return
        self.app.opt.auto_scale = False
        self.tkopt.auto_scale.set(False)
        self._updateCardSize()

    def mDecreaseCardset(self, *event):
        if self._cancelDrag(break_pause=True): return
        if self.app.opt.scale_x > 0.5:
            self.app.opt.scale_x -= 0.1
        else:
            return
        if self.app.opt.scale_y > 0.5:
            self.app.opt.scale_y -= 0.1
        else:
            return
        self.app.opt.auto_scale = False
        self.tkopt.auto_scale.set(False)
        self._updateCardSize()

    def mOptAutoScale(self, *event):
        if self._cancelDrag(break_pause=True): return
        auto_scale = not self.app.opt.auto_scale
        self.app.opt.auto_scale = auto_scale
        self.tkopt.auto_scale.set(auto_scale)
        self._updateCardSize()

    def mSelectCardsetDialog(self, *event):
        if self._cancelDrag(break_pause=False): return
        ##strings, default = ("&OK", "&Load", "&Cancel"), 0
        strings, default = (None, _("&Load"), _("&Cancel"),), 1
        ##if os.name == "posix":
        strings, default = (None, _("&Load"), _("&Cancel"), _("&Info..."),), 1
        t = CARDSET
        key = self.app.nextgame.cardset.index
        d = SelectCardsetDialogWithPreview(self.top, title=_("Select ")+t,
                app=self.app, manager=self.app.cardset_manager, key=key,
                strings=strings, default=default)
        cs = self.app.cardset_manager.get(d.key)
        if d.status != 0 or d.button != 1 or cs is None:
            return
        if USE_PIL:
            changed = (self.app.opt.scale_x,
                       self.app.opt.scale_y,
                       self.app.opt.auto_scale,
                       self.app.opt.preserve_aspect_ratio) != d.scale_values
        else:
            changed = False
        if d.key == self.app.cardset.index and not changed:
            return
        if d.key >= 0:
            self.app.nextgame.cardset = cs
            if USE_PIL:
                (self.app.opt.scale_x,
                 self.app.opt.scale_y,
                 self.app.opt.auto_scale,
                 self.app.opt.preserve_aspect_ratio) = d.scale_values
                if not self.app.opt.auto_scale:
                    self.app.images.resize(self.app.opt.scale_x,
                                           self.app.opt.scale_y)
            self._cancelDrag()
            self.game.endGame(bookmark=1)
            self.game.quitGame(bookmark=1)

    def _mOptCardback(self, index):
        if self._cancelDrag(break_pause=False): return
        cs = self.app.cardset
        old_index = cs.backindex
        cs.updateCardback(backindex=index)
        if cs.backindex == old_index:
            return
        self.app.updateCardset(self.game.id)
        image = self.app.images.getBack(update=True)
        for card in self.game.cards:
            card.updateCardBackground(image=image)
        self.app.canvas.update_idletasks()
        self.tkopt.cardback.set(cs.backindex)

    def mOptCardback(self, *event):
        self._mOptCardback(self.tkopt.cardback.get())

    def mOptChangeCardback(self, *event):
        self._mOptCardback(self.app.cardset.backindex + 1)

    def mOptChangeTableTile(self, *event):
        if self._cancelDrag(break_pause=False): return
        n = self.app.tabletile_manager.len()
        if n >= 2:
            i = (self.tkopt.tabletile.get() + 1) % n
            if self.app.setTile(i):
                self.tkopt.tabletile.set(i)

    def mSelectTileDialog(self, *event):
        if self._cancelDrag(break_pause=False): return
        key = self.app.tabletile_index
        if key <= 0:
            key = self.app.opt.colors['table'] ##.lower()
        d = SelectTileDialogWithPreview(self.top, app=self.app,
                                        title=_("Select table background"),
                                        manager=self.app.tabletile_manager,
                                        key=key)
        if d.status == 0 and d.button == 0:
            if isinstance(d.key, str):
                tile = self.app.tabletile_manager.get(0)
                tile.color = d.key
                if self.app.setTile(0):
                    self.tkopt.tabletile.set(0)
            elif d.key > 0 and d.key != self.app.tabletile_index:
                if self.app.setTile(d.key):
                    self.tkopt.tabletile.set(d.key)

    def mOptToolbar(self, *event):
        ##if self._cancelDrag(break_pause=False): return
        self.setToolbarSide(self.tkopt.toolbar.get())

    def mOptToolbarStyle(self, *event):
        ##if self._cancelDrag(break_pause=False): return
        self.setToolbarStyle(self.tkopt.toolbar_style.get())

    def mOptToolbarCompound(self, *event):
        ##if self._cancelDrag(break_pause=False): return
        self.setToolbarCompound(self.tkopt.toolbar_compound.get())

    def mOptToolbarSize(self, *event):
        ##if self._cancelDrag(break_pause=False): return
        self.setToolbarSize(self.tkopt.toolbar_size.get())

    def mOptToolbarRelief(self, *event):
        ##if self._cancelDrag(break_pause=False): return
        self.setToolbarRelief(self.tkopt.toolbar_relief.get())

    def mOptToolbarConfig(self, w):
        self.toolbarConfig(w, self.tkopt.toolbar_vars[w].get())

    def mOptStatusbar(self, *event):
        if self._cancelDrag(break_pause=False): return
        if not self.app.statusbar: return
        side = self.tkopt.statusbar.get()
        self.app.opt.statusbar = side
        resize = not self.app.opt.save_games_geometry
        if self.app.statusbar.show(side, resize=resize):
            self.top.update_idletasks()

    def mOptNumCards(self, *event):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.num_cards = self.tkopt.num_cards.get()

    def mOptHelpbar(self, *event):
        if self._cancelDrag(break_pause=False): return
        if not self.app.helpbar: return
        show = self.tkopt.helpbar.get()
        self.app.opt.helpbar = show
        resize = not self.app.opt.save_games_geometry
        if self.app.helpbar.show(show, resize=resize):
            self.top.update_idletasks()

    def mOptSaveGamesGeometry(self, *event):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.save_games_geometry = self.tkopt.save_games_geometry.get()

    def mOptDemoLogo(self, *event):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.demo_logo = self.tkopt.demo_logo.get()

    def mOptSplashscreen(self, *event):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.splashscreen = self.tkopt.splashscreen.get()

    def mOptMouseType(self, *event):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.mouse_type = self.tkopt.mouse_type.get()

    def mOptMouseUndo(self, *event):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.mouse_undo = self.tkopt.mouse_undo.get()

    def mOptNegativeBottom(self, *event):
        if self._cancelDrag(): return
        self.app.opt.negative_bottom = self.tkopt.negative_bottom.get()
        self.app.updateCardset()
        self.game.endGame(bookmark=1)
        self.game.quitGame(bookmark=1)


    #
    # toolbar support
    #

    def setToolbarSide(self, side):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.toolbar = side
        self.tkopt.toolbar.set(side)                    # update radiobutton
        resize = not self.app.opt.save_games_geometry
        if self.app.toolbar.show(side, resize=resize):
            self.top.update_idletasks()

    def setToolbarSize(self, size):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.toolbar_size = size
        self.tkopt.toolbar_size.set(size)                # update radiobutton
        dir = self.app.getToolbarImagesDir()
        if self.app.toolbar.updateImages(dir, size):
            self.game.updateStatus(player=self.app.opt.player)
            self.top.update_idletasks()

    def setToolbarStyle(self, style):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.toolbar_style = style
        self.tkopt.toolbar_style.set(style)                # update radiobutton
        dir = self.app.getToolbarImagesDir()
        size = self.app.opt.toolbar_size
        if self.app.toolbar.updateImages(dir, size):
            ##self.game.updateStatus(player=self.app.opt.player)
            self.top.update_idletasks()

    def setToolbarCompound(self, compound):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.toolbar_compound = compound
        self.tkopt.toolbar_compound.set(compound)          # update radiobutton
        if self.app.toolbar.setCompound(compound):
            self.game.updateStatus(player=self.app.opt.player)
            self.top.update_idletasks()

    def setToolbarRelief(self, relief):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.toolbar_relief = relief
        self.tkopt.toolbar_relief.set(relief)           # update radiobutton
        self.app.toolbar.setRelief(relief)
        self.top.update_idletasks()

    def toolbarConfig(self, w, v):
        if self._cancelDrag(break_pause=False): return
        self.app.opt.toolbar_vars[w] = v
        self.app.toolbar.config(w, v)
        self.top.update_idletasks()

    #
    # stacks descriptions
    #

    def mStackDesk(self, *event):
        if self.game.stackdesc_list:
            self.game.deleteStackDesc()
        else:
            if self._cancelDrag(break_pause=True): return
            self.game.showStackDesc()


    def wizardDialog(self, edit=False):
        from pysollib.wizardutil import write_game, reset_wizard
        from wizarddialog import WizardDialog

        if edit:
            reset_wizard(self.game)
        else:
            reset_wizard(None)
        d = WizardDialog(self.top, _('Solitaire Wizard'), self.app)
        if d.status == 0 and d.button == 0:
            try:
                if edit:
                    gameid = write_game(self.app, game=self.game)
                else:
                    gameid = write_game(self.app)
            except Exception, err:
                if DEBUG:
                    traceback.print_exc()
                d = MfxMessageDialog(self.top, title=_('Save game error'),
                                     text=_('''
Error while saving game.

%s
''') % str(err),
                                     bitmap='error')
                return
            if SELECT_GAME_MENU:
                menu = self.menupath[".menubar.select.customgames"][2]
                select_func = lambda gi: gi.si.game_type == GI.GT_CUSTOM
                games = map(self.app.gdb.get,
                            self.app.gdb.getGamesIdSortedByName())
                games = filter(select_func, games)
                self.updateGamesMenu(menu, games)

            self.tkopt.gameid.set(gameid)
            self._mSelectGame(gameid, force=True)


    def mWizard(self, *event):
        if self._cancelDrag(break_pause=False): return
        self.wizardDialog()

    def mWizardEdit(self, *event):
        if self._cancelDrag(break_pause=False): return
        self.wizardDialog(edit=True)

