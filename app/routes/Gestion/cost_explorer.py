from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
import boto3
import os
from datetime import datetime, timedelta

cost_explorer = Blueprint('cost_explorer', __name__)

@cost_explorer.route('/cost_explorer')
def cost_explorer_dashboard():
    """Dashboard principal de Cost Explorer"""
    return render_template('Gestion/cost_explorer/index.html')

@cost_explorer.route('/cost_explorer/costs', methods=['GET', 'POST'])
def get_costs():
    """Obtener costos de AWS"""
    if request.method == 'POST':
        try:
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')

            if not start_date or not end_date:
                flash('Las fechas de inicio y fin son requeridas', 'error')
                return redirect(url_for('cost_explorer.get_costs'))

            # Cost Explorer solo funciona en us-east-1
            ce = boto3.client('ce', region_name='us-east-1')

            response = ce.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost']
            )

            costs = []
            for result in response['ResultsByTime']:
                costs.append({
                    'period': f"{result['TimePeriod']['Start']} - {result['TimePeriod']['End']}",
                    'amount': result['Total']['UnblendedCost']['Amount'],
                    'unit': result['Total']['UnblendedCost']['Unit']
                })

            return render_template('Gestion/cost_explorer/costs.html',
                                 costs=costs,
                                 start_date=start_date,
                                 end_date=end_date)

        except Exception as e:
            flash(f'Error obteniendo costos: {str(e)}', 'error')
            return redirect(url_for('cost_explorer.get_costs'))

    # GET request - mostrar formulario
    today = datetime.now()
    start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')

    return render_template('Gestion/cost_explorer/costs.html',
                         costs=None,
                         start_date=start_date,
                         end_date=end_date)

@cost_explorer.route('/cost_explorer/forecast', methods=['GET', 'POST'])
def get_cost_forecast():
    """Obtener pronóstico de costos"""
    if request.method == 'POST':
        try:
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            prediction_interval_level = request.form.get('prediction_interval_level', 80)

            if not start_date or not end_date:
                flash('Las fechas de inicio y fin son requeridas', 'error')
                return redirect(url_for('cost_explorer.get_cost_forecast'))

            # Cost Explorer solo funciona en us-east-1
            ce = boto3.client('ce', region_name='us-east-1')

            response = ce.get_cost_forecast(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Metric='UNBLENDED_COST',
                Granularity='MONTHLY',
                PredictionIntervalLevel=int(prediction_interval_level)
            )

            forecast = []
            for result in response['ForecastResultsByTime']:
                forecast.append({
                    'period': f"{result['TimePeriod']['Start']} - {result['TimePeriod']['End']}",
                    'amount': result['MeanValue'],
                    'unit': result['Unit'],
                    'prediction_interval_lower': result.get('PredictionIntervalLowerBound'),
                    'prediction_interval_upper': result.get('PredictionIntervalUpperBound')
                })

            return render_template('Gestion/cost_explorer/forecast.html',
                                 forecast=forecast,
                                 start_date=start_date,
                                 end_date=end_date,
                                 prediction_interval_level=prediction_interval_level)

        except Exception as e:
            flash(f'Error obteniendo pronóstico de costos: {str(e)}', 'error')
            return redirect(url_for('cost_explorer.get_cost_forecast'))

    # GET request - mostrar formulario
    today = datetime.now()
    start_date = today.strftime('%Y-%m-%d')
    end_date = (today + timedelta(days=30)).strftime('%Y-%m-%d')

    return render_template('Gestion/cost_explorer/forecast.html',
                         forecast=None,
                         start_date=start_date,
                         end_date=end_date,
                         prediction_interval_level=80)

@cost_explorer.route('/cost_explorer/categories', methods=['GET', 'POST'])
def get_cost_categories():
    """Obtener categorías de costos"""
    if request.method == 'POST':
        try:
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            max_results = int(request.form.get('max_results', 10))

            if not start_date or not end_date:
                flash('Las fechas de inicio y fin son requeridas', 'error')
                return redirect(url_for('cost_explorer.get_cost_categories'))

            # Cost Explorer solo funciona en us-east-1
            ce = boto3.client('ce', region_name='us-east-1')

            response = ce.get_cost_and_usage_with_resources(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }
                ]
            )

            categories = []
            for group in response['ResultsByTime'][0]['Groups'][:max_results]:
                categories.append({
                    'service': group['Keys'][0],
                    'amount': group['Metrics']['UnblendedCost']['Amount'],
                    'unit': group['Metrics']['UnblendedCost']['Unit']
                })

            # Ordenar por monto descendente
            categories.sort(key=lambda x: float(x['amount']), reverse=True)

            return render_template('Gestion/cost_explorer/categories.html',
                                 categories=categories,
                                 start_date=start_date,
                                 end_date=end_date,
                                 max_results=max_results)

        except Exception as e:
            flash(f'Error obteniendo categorías de costos: {str(e)}', 'error')
            return redirect(url_for('cost_explorer.get_cost_categories'))

    # GET request - mostrar formulario
    today = datetime.now()
    start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')

    return render_template('Gestion/cost_explorer/categories.html',
                         categories=None,
                         start_date=start_date,
                         end_date=end_date,
                         max_results=10)

@cost_explorer.route('/cost_explorer/savings_plans', methods=['GET', 'POST'])
def get_savings_plans_utilization():
    """Obtener utilización de Savings Plans"""
    if request.method == 'POST':
        try:
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')

            if not start_date or not end_date:
                flash('Las fechas de inicio y fin son requeridas', 'error')
                return redirect(url_for('cost_explorer.get_savings_plans_utilization'))

            # Cost Explorer solo funciona en us-east-1
            ce = boto3.client('ce', region_name='us-east-1')

            response = ce.get_savings_plans_utilization(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                }
            )

            savings_plans = []
            for sp in response['SavingsPlansUtilizationsByTime']:
                savings_plans.append({
                    'period': f"{sp['TimePeriod']['Start']} - {sp['TimePeriod']['End']}",
                    'total_commitment': sp['Total']['TotalCommitment'],
                    'used_commitment': sp['Total']['UsedCommitment'],
                    'unused_commitment': sp['Total']['UnusedCommitment'],
                    'utilization_percentage': sp['Total']['UtilizationPercentage'],
                    'unit': sp['Total']['Unit']
                })

            return render_template('Gestion/cost_explorer/savings_plans.html',
                                 savings_plans=savings_plans,
                                 start_date=start_date,
                                 end_date=end_date)

        except Exception as e:
            flash(f'Error obteniendo utilización de Savings Plans: {str(e)}', 'error')
            return redirect(url_for('cost_explorer.get_savings_plans_utilization'))

    # GET request - mostrar formulario
    today = datetime.now()
    start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')

    return render_template('Gestion/cost_explorer/savings_plans.html',
                         savings_plans=None,
                         start_date=start_date,
                         end_date=end_date)