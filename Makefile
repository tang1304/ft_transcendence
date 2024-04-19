# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: cbernot <cbernot@student.42lyon.fr>        +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/04/04 10:39:53 by cbernot           #+#    #+#              #
#    Updated: 2024/04/04 10:44:08 by cbernot          ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

.PHONY: all stop clean fclean re

# ------------------------------------------------------------------------------
# COMMAND VARIABLES
# ------------------------------------------------------------------------------

LOGIN			=	cbernot
VOL_PATH		=	/home/$(LOGIN)/data/
YML_PATH		=	backend/docker-compose.yml
DJANGO_PATH		=	backend/django
POSTGRESQL_PATH	=	backend/postgresql

RM			=	rm -rf

# Colors
BLACK		=	\033[30m
RED			=	\033[31m
GREEN		=	\033[32m
YELLOW		=	\033[33m
BLUE		=	\033[34m
PURPLE		=	\033[35m
CYAN		=	\033[36m

# Text
ERASE		=	\033[2K\r
RESET		=	\033[0m
BOLD		=	\033[1m
FAINT		=	\033[2m
ITALIC		=	\033[3m
UNDERLINE	=	\033[4m

# ------------------------------------------------------------------------------
# RULES
# ------------------------------------------------------------------------------

all:
# @sudo mkdir -p $(VOL_PATH)wordpress
# @echo "$(ERASE)$(GREEN) ✔$(RESET) directory $(VOL_PATH)wordpress\t$(GREEN)created$(RESET)"
# @sudo mkdir -p $(VOL_PATH)mariadb
# @echo "$(ERASE)$(GREEN) ✔$(RESET) directory $(VOL_PATH)mariadb\t$(GREEN)created$(RESET)"
# @sudo chmod 777 $(VOL_PATH)wordpress
# @sudo chmod 777 $(VOL_PATH)mariadb
# @echo "$(ERASE)$(GREEN) ✔$(RESET) granted writing rights\t\t\t\t\t$(GREEN)done$(RESET)"
	sudo docker compose -f $(YML_PATH) up --build

stop:
	sudo docker compose -f $(YML_PATH) stop

# Cleaning
clean:
	sudo docker compose -f $(YML_PATH) down -v

fclean: clean
# @sudo rm -rf $(VOL_PATH)wordpress
# @echo "$(ERASE)$(GREEN) ✔$(RESET) directory $(VOL_PATH)wordpress\t$(YELLOW)deleted$(RESET)"
# @sudo rm -rf $(VOL_PATH)mariadb
# @echo "$(ERASE)$(GREEN) ✔$(RESET) directory $(VOL_PATH)mariadb\t$(YELLOW)deleted$(RESET)"
	sudo docker system prune -af --volumes
	@echo "$(ERASE)$(GREEN) ✔$(RESET) docker containers, images, volumes, networks and cache\t$(YELLOW)deleted$(RESET)"

re: fclean all