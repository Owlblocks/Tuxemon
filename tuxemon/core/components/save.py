# -*- coding: utf-8 -*-
#
# Tuxemon
# Copyright (C) 2014, William Edwards <shadowapex@gmail.com>,
#                     Benjamin Bean <superman2k5@gmail.com>
#
# This file is part of Tuxemon.
#
# Tuxemon is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Tuxemon is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Tuxemon.  If not, see <http://www.gnu.org/licenses/>.
#
# Contributor(s):
#
# William Edwards <shadowapex@gmail.com>
#
#
# core.components.save Handle save games.
#
#

import base64
import json
import datetime
import logging

import pygame

from tuxemon.core import prepare

try:
    import cbor
except ImportError:
    prepare.SAVE_METHOD = "JSON"

# Create a logger for optional handling of debug messages.
logger = logging.getLogger(__name__)


def get_save_data(game):
    """Gets a dictionary which represents the state of the game.

    :param game: The core.control.Control object that runs the game.
    :type game: core.control.Control

    :rtype: Dictionary
    :returns: Game data to save, must be JSON encodable.

    """
    save_data = game.player1.get_state(game)
    screenshot = capture_screenshot(game)
    save_data['screenshot'] = base64.encodestring(pygame.image.tostring(screenshot, "RGB"))
    save_data['screenshot_width'] = screenshot.get_width()
    save_data['screenshot_height'] = screenshot.get_height()
    save_data['time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return save_data


def capture_screenshot(game):
    screenshot = pygame.Surface(game.screen.get_size())
    world = game.get_state_name("WorldState")
    world.draw(screenshot)
    return screenshot


def save(save_data, slot):
    """Saves the current game state to a file using shelve.

    :param save_data: The data to save.
    :param screenshot: An image of the current frame
    :param slot: The save slot to save the data to.

    :type save_data: Dictionary
    :type screenshot: pygame.Image
    :type slot: Integer

    :rtype: None
    :returns: None

    """
    # Save a screenshot of the current frame
    save_path = prepare.SAVE_PATH + str(slot) + '.save'
    if prepare.SAVE_METHOD == "CBOR":
        text = cbor.dumps(save_data)
    else:
        text = json.dumps(save_data)
    with open(save_path, 'w') as f:
        logger.info("Saving data to save file: " + save_path)
        # Don't dump straight to the file: if we crash it would corrupt the save_data
        f.write(text)


def load(slot):
    """Loads game state data from a shelved save file.

    :param slot: The save slot to load game data from.
    :type slot: Integer

    :rtype: Dictionary
    :returns: Dictionary containing game data to load.

    **Examples:**

    >>> core.components.load.load(1)

    """

    save_path = prepare.SAVE_PATH + str(slot) + '.save'
    save_data = dict()
    try:
        with open(save_path, 'r') as save_file:
            text = save_file.read()

            try:
                return json.loads(text)
            except ValueError as e:
                logger.error("cannot decode JSON: %s", save_path)

            if prepare.SAVE_METHOD == "CBOR":
                try:
                    return cbor.loads(text)
                except ValueError as e:
                    logger.error("cannot decode save CBOR: %s", save_path)
            else:
                pass

    except IOError as e:
        logger.error(e)

    save_data["error"] = "Save file corrupted"
    save_data["player_name"] = "BROKEN SAVE!"
    logger.error("Failed loading save file.")
    return save_data

