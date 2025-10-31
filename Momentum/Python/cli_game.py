"""
Command Line Interface for Momentum Motorsport Manager

Terminal-based game interface using Rich library for output.
This is an actual playable game.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.text import Text
from rich import box
from typing import Optional, List
import sys

from systems.world_state import GameWorld, PlayerProfile
from database.database_manager import DatabaseManager
from database.models import Team, Driver, Track, Race
from disciplines.race_simulation import RaceSimulator, SimulationContext


console = Console()


class MomentumCLI:
    """Command line interface for the game"""
    
    def __init__(self):
        """Initialize the CLI"""
        self.world = GameWorld()
        self.db = DatabaseManager()
        self.simulator = RaceSimulator()
        self.running = True
        
    def clear_screen(self):
        """Clear the terminal screen"""
        console.clear()
    
    def show_title(self):
        """Display game title"""
        title = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     MOMENTUM - MOTORSPORT MANAGEMENT SIMULATION           ║
║                                                           ║
║              Terminal Edition v0.1.0                      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
        """
        console.print(title, style="bold cyan")
    
    def main_menu(self):
        """Display main menu"""
        self.clear_screen()
        self.show_title()
        
        console.print("\n[bold]Main Menu[/bold]\n", justify="center")
        
        choices = [
            "1. New Career",
            "2. Load Career",
            "3. Quick Race (Single Race Mode)",
            "4. Exit"
        ]
        
        for choice in choices:
            console.print(f"  {choice}")
        
        console.print()
        choice = Prompt.ask("Select option", choices=["1", "2", "3", "4"])
        
        if choice == "1":
            self.new_career_flow()
        elif choice == "2":
            self.load_career_flow()
        elif choice == "3":
            self.quick_race_flow()
        elif choice == "4":
            self.running = False
    
    def new_career_flow(self):
        """Start a new career"""
        self.clear_screen()
        console.print("\n[bold cyan]═══ NEW CAREER ═══[/bold cyan]\n")
        
        # Get player name
        player_name = Prompt.ask("Enter your name")
        
        # Create new game
        self.world.new_game(player_name)
        
        console.print(f"\n[green]Welcome to Momentum, {player_name}![/green]")
        console.print("\nYou're about to start your motorsport management career.")
        console.print("First, you need to select a team to manage.\n")
        
        input("Press Enter to continue...")
        
        # Team selection
        if self.team_selection_screen():
            # Season creation
            self.season_creation_screen()
            # Enter career mode
            self.career_mode_loop()
        else:
            console.print("[red]Failed to select team. Returning to main menu.[/red]")
            input("Press Enter to continue...")
    
    def team_selection_screen(self) -> bool:
        """
        Team selection screen
        
        Returns:
            True if team selected successfully
        """
        self.clear_screen()
        console.print("\n[bold cyan]═══ TEAM SELECTION ═══[/bold cyan]\n")
        
        # Get available teams (tier 3 for starting)
        # NOTE: This will likely fail because we don't have a get_teams_by_tier method yet
        # Let's just get ANY teams for now
        console.print("[yellow]Loading available teams...[/yellow]")
        
        try:
            # Try to get single seater teams
            teams = self.db.get_teams_by_discipline("SINGLE_SEATER")
            
            if not teams:
                console.print("[red]ERROR: No teams found in database![/red]")
                return False
            
            # Show first 20 teams only
            display_teams = teams[:20]
            
            # Create table
            table = Table(title="Available Teams", box=box.ROUNDED)
            table.add_column("ID", style="cyan", width=6)
            table.add_column("Team Name", style="white", width=30)
            table.add_column("Nationality", width=10)
            table.add_column("Budget", style="green", width=15)
            table.add_column("Tier", width=8)
            
            for team in display_teams:
                budget_str = f"€{team.budget:,.0f}M"
                table.add_row(
                    str(team.id),
                    team.name,
                    team.nationality,
                    budget_str,
                    team.tier
                )
            
            console.print(table)
            console.print(f"\n[dim]Showing {len(display_teams)} of {len(teams)} teams[/dim]")
            
            # Get team selection
            team_id = Prompt.ask(
                "\nEnter team ID to manage",
                choices=[str(t.id) for t in display_teams]
            )
            
            # Select team
            if self.world.select_team(int(team_id)):
                selected_team = self.db.get_team(int(team_id))
                console.print(f"\n[green]✓ You are now managing {selected_team.name}![/green]")
                input("\nPress Enter to continue...")
                return True
            else:
                return False
                
        except Exception as e:
            console.print(f"[red]ERROR: {str(e)}[/red]")
            console.print("\n[yellow]This is expected - database queries need refinement[/yellow]")
            return False
    
    def season_creation_screen(self):
        """Create a new championship season"""
        self.clear_screen()
        console.print("\n[bold cyan]═══ SEASON SETUP ═══[/bold cyan]\n")
        
        # For now, just create a simple single-seater championship
        discipline = "SINGLE_SEATER"
        num_races = 10
        
        console.print(f"Creating {discipline} championship with {num_races} races...")
        
        try:
            champ = self.world.create_championship_season(
                discipline=discipline,
                num_races=num_races
            )
            
            if champ:
                console.print(f"\n[green]✓ Season created successfully![/green]")
                console.print(f"Championship: {champ.name}")
                console.print(f"Races: {len(self.world.current_season_races)}")
            else:
                console.print("[red]Failed to create season[/red]")
                
        except Exception as e:
            console.print(f"[red]ERROR: {str(e)}[/red]")
            console.print("\n[yellow]This reveals issues with race calendar generation[/yellow]")
        
        input("\nPress Enter to continue...")
    
    def career_mode_loop(self):
        """Main career mode game loop"""
        while self.running:
            self.clear_screen()
            
            # Show current status
            self.show_career_status()
            
            # Show menu
            console.print("\n[bold]Career Menu[/bold]\n")
            
            if not self.world.is_season_complete():
                choices = [
                    "1. Next Race Weekend",
                    "2. View Championship Standings",
                    "3. View Team",
                    "4. View Calendar",
                    "5. Save Game",
                    "6. Exit to Main Menu"
                ]
            else:
                choices = [
                    "1. End Season & Start New Season",
                    "2. View Final Standings",
                    "3. View Season Summary",
                    "4. Save Game",
                    "5. Exit to Main Menu"
                ]
            
            for choice in choices:
                console.print(f"  {choice}")
            
            console.print()
            max_choice = str(len(choices))
            choice = Prompt.ask("Select option", choices=[str(i+1) for i in range(len(choices))])
            
            # Handle choice
            if not self.world.is_season_complete():
                if choice == "1":
                    self.race_weekend_flow()
                elif choice == "2":
                    self.view_standings()
                elif choice == "3":
                    self.view_team()
                elif choice == "4":
                    self.view_calendar()
                elif choice == "5":
                    self.save_game()
                elif choice == "6":
                    break
            else:
                if choice == "1":
                    self.advance_season()
                elif choice == "2":
                    self.view_standings()
                elif choice == "3":
                    console.print("[yellow]Season summary not implemented yet[/yellow]")
                    input("Press Enter...")
                elif choice == "4":
                    self.save_game()
                elif choice == "5":
                    break
    
    def show_career_status(self):
        """Display current career status"""
        if not self.world.state:
            return
        
        summary = self.world.get_state_summary()
        
        status_panel = Panel(
            f"[cyan]Date:[/cyan] {summary['current_date']}\n"
            f"[cyan]Season:[/cyan] {summary['season']} ({summary['calendar_year']})\n"
            f"[cyan]Current Race:[/cyan] {summary['current_race']}\n"
            f"[cyan]Player:[/cyan] {summary['player_name']}",
            title="Career Status",
            border_style="cyan"
        )
        
        console.print(status_panel)
    
    def race_weekend_flow(self):
        """Execute a race weekend"""
        self.clear_screen()
        console.print("\n[bold cyan]═══ RACE WEEKEND ═══[/bold cyan]\n")
        
        # Get next race
        next_race = self.world.get_next_race()
        
        if not next_race:
            console.print("[red]No race available![/red]")
            input("Press Enter...")
            return
        
        # Advance to race date
        self.world.advance_to_next_race()
        
        # Get track info
        track = self.db.get_track(next_race.track_id)
        
        console.print(f"[bold]Round {next_race.round_number}[/bold]")
        console.print(f"Track: {track.name}")
        console.print(f"Country: {track.country}")
        console.print(f"Date: {next_race.race_date}")
        console.print()
        
        # Simplified race execution
        if Confirm.ask("Simulate race?"):
            console.print("\n[yellow]Simulating race...[/yellow]")
            
            try:
                # NOTE: This will likely fail because we need:
                # 1. Get teams in championship
                # 2. Get drivers for each team
                # 3. Create proper simulation context
                # Let's try anyway and see what breaks
                
                # For now, just mark race as complete
                console.print("[yellow]Race simulation integration not complete yet[/yellow]")
                console.print("Marking race as completed...")
                
                self.world.complete_race(next_race.id)
                
                console.print("\n[green]✓ Race completed![/green]")
                
            except Exception as e:
                console.print(f"[red]ERROR: {str(e)}[/red]")
                console.print("\n[yellow]This shows what needs to be fixed in race integration[/yellow]")
        
        input("\nPress Enter to continue...")
    
    def view_standings(self):
        """View championship standings"""
        self.clear_screen()
        console.print("\n[bold cyan]═══ CHAMPIONSHIP STANDINGS ═══[/bold cyan]\n")
        
        console.print("[yellow]Standings display not implemented yet[/yellow]")
        console.print("Need to:")
        console.print("  - Query race results from database")
        console.print("  - Calculate points totals")
        console.print("  - Sort by points")
        console.print("  - Display in table format")
        
        input("\nPress Enter to continue...")
    
    def view_team(self):
        """View player's team"""
        self.clear_screen()
        console.print("\n[bold cyan]═══ YOUR TEAM ═══[/bold cyan]\n")
        
        if not self.world.state or not self.world.state.player_profile:
            console.print("[red]No player data[/red]")
            input("Press Enter...")
            return
        
        team = self.db.get_team(self.world.state.player_profile.team_id)
        
        if team:
            team_panel = Panel(
                f"[bold]{team.name}[/bold]\n\n"
                f"Nationality: {team.nationality}\n"
                f"Discipline: {team.discipline}\n"
                f"Tier: {team.tier}\n"
                f"Budget: €{team.budget:,.0f}M\n"
                f"Founded: {team.founded_year}",
                border_style="cyan"
            )
            console.print(team_panel)
            
            # TODO: Show drivers, staff, etc.
            console.print("\n[dim]Driver and staff management coming soon...[/dim]")
        
        input("\nPress Enter to continue...")
    
    def view_calendar(self):
        """View season calendar"""
        self.clear_screen()
        console.print("\n[bold cyan]═══ SEASON CALENDAR ═══[/bold cyan]\n")
        
        if not self.world.current_season_races:
            console.print("[red]No active season[/red]")
            input("Press Enter...")
            return
        
        table = Table(title="Race Calendar", box=box.ROUNDED)
        table.add_column("Round", style="cyan", width=6)
        table.add_column("Date", width=12)
        table.add_column("Track", style="white", width=30)
        table.add_column("Status", width=12)
        
        for race in self.world.current_season_races:
            track = self.db.get_track(race.track_id)
            track_name = track.name if track else "Unknown"
            
            # Determine status display
            if race.status == "completed":
                status = "[green]Completed[/green]"
            elif race.status == "scheduled":
                status = "[yellow]Scheduled[/yellow]"
            else:
                status = race.status
            
            table.add_row(
                str(race.round_number),
                race.race_date,
                track_name,
                status
            )
        
        console.print(table)
        input("\nPress Enter to continue...")
    
    def advance_season(self):
        """Advance to next season"""
        self.clear_screen()
        console.print("\n[bold cyan]═══ END OF SEASON ═══[/bold cyan]\n")
        
        console.print("[yellow]Season completion and progression not implemented yet[/yellow]")
        console.print("\nNeeds:")
        console.print("  - Final standings calculation")
        console.print("  - Champion determination")
        console.print("  - End-of-season summary")
        console.print("  - Driver/team evolution")
        console.print("  - Contract renewals")
        
        if Confirm.ask("\nAdvance to next season anyway?"):
            self.world.advance_season()
            self.season_creation_screen()
        
        input("\nPress Enter...")
    
    def save_game(self):
        """Save current game"""
        console.print("\n[cyan]Saving game...[/cyan]")
        
        if self.world.save_game():
            console.print("[green]✓ Game saved successfully![/green]")
        else:
            console.print("[red]Failed to save game[/red]")
        
        input("Press Enter...")
    
    def load_career_flow(self):
        """Load saved career"""
        self.clear_screen()
        console.print("\n[bold cyan]═══ LOAD CAREER ═══[/bold cyan]\n")
        
        saves = self.world.list_saves()
        
        if not saves:
            console.print("[yellow]No saved games found[/yellow]")
            input("Press Enter...")
            return
        
        console.print("Available saves:\n")
        for i, save in enumerate(saves, 1):
            console.print(f"  {i}. {save}")
        
        console.print()
        choice = Prompt.ask("Select save", choices=[str(i+1) for i in range(len(saves))] + ["0"])
        
        if choice == "0":
            return
        
        save_name = saves[int(choice) - 1]
        
        if self.world.load_game(save_name):
            console.print(f"\n[green]✓ Loaded {save_name}[/green]")
            input("Press Enter...")
            self.career_mode_loop()
        else:
            console.print("[red]Failed to load game[/red]")
            input("Press Enter...")
    
    def quick_race_flow(self):
        """Quick race mode (single race, no career)"""
        self.clear_screen()
        console.print("\n[bold cyan]═══ QUICK RACE ═══[/bold cyan]\n")
        
        console.print("[yellow]Quick race mode not implemented yet[/yellow]")
        console.print("\nThis would let you:")
        console.print("  - Select a track")
        console.print("  - Select teams/drivers")
        console.print("  - Run a single race")
        console.print("  - See results")
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Main run loop"""
        while self.running:
            try:
                self.main_menu()
            except KeyboardInterrupt:
                console.print("\n\n[yellow]Interrupted by user[/yellow]")
                if Confirm.ask("Exit game?"):
                    self.running = False
            except Exception as e:
                console.print(f"\n[red]ERROR: {str(e)}[/red]")
                console.print("\n[yellow]This helps us identify what needs fixing![/yellow]")
                import traceback
                traceback.print_exc()
                input("\nPress Enter to continue...")
        
        console.print("\n[cyan]Thanks for playing Momentum![/cyan]\n")


def main():
    """Entry point"""
    game = MomentumCLI()
    game.run()


if __name__ == "__main__":
    main()
